-- reaper/midi_drums/sections.lua
-- Common helpers and Python CLI command builders for the REAPER panel.
-- All functions use our midi-drums CLI contract (not fsecada's API).

local M = {}

-- ===== Project helpers =====

function M.get_project_dir()
  local p = reaper.GetProjectPath("")
  return (p ~= "") and p or reaper.GetResourcePath()
end

function M.shell_escape(s)
  s = s:gsub("[\r\n]", " ")
  s = s:gsub('"', "'")
  s = s:gsub("[&|^<>%%]", "")
  return s
end

-- ===== Sidecar parsing =====

function M.parse_sidecar(content)
  local tempo = tonumber(content:match('"tempo"%s*:%s*([%d%.]+)'))
  if not tempo then
    return nil, nil, nil, nil, "Could not parse 'tempo'."
  end
  local ts_num, ts_denom = content:match(
    '"time_signature"%s*:%s*%[%s*(%d+)%s*,%s*(%d+)%s*%]'
  )
  ts_num   = tonumber(ts_num)   or 4
  ts_denom = tonumber(ts_denom) or 4
  local sections_list = {}
  for name, bars in content:gmatch(
    '"name"%s*:%s*"([^"]+)"%s*,%s*"bars"%s*:%s*(%d+)'
  ) do
    sections_list[#sections_list + 1] = { name = name, bars = tonumber(bars) }
  end
  if #sections_list == 0 then
    return nil, nil, nil, nil, "No sections found."
  end
  return tempo, ts_num, ts_denom, sections_list
end

-- ===== Sidecar writing =====

function M.sections_to_json(sections_list, bpm, num, denom)
  local sb = { "{", string.format('"tempo": %d,', bpm) }
  sb[#sb + 1] = string.format('"time_signature": [%d, %d],', num or 4, denom or 4)
  sb[#sb + 1] = '"sections": ['
  for i, sec in ipairs(sections_list) do
    sb[#sb + 1] = string.format('{"name": "%s", "bars": %d}',
      sec.name:gsub('"', "'"), sec.bars)
    if i < #sections_list then sb[#sb + 1] = ', ' end
  end
  sb[#sb + 1] = ']'
  sb[#sb + 1] = "}"
  return table.concat(sb)
end

-- ===== Region creation =====

function M.create_regions_from_sections(sections_list, bpm, num, denom)
  local prev_pos = -1
  for _, sec in ipairs(sections_list) do
    local duration_beats = (bpm and (60.0 / bpm * sec.bars * 4.0)) or (sec.bars * 4.0)
    local pos = prev_pos + 1
    if num and denom then
      -- Convert beats to seconds using tempo
      local quarter_note_time = 60.0 / bpm
      local beats_per_bar = num
      local duration_seconds = sec.bars * (quarter_note_time * beats_per_bar)
      pos = prev_pos + duration_seconds
    end

    reaper.SetProjectMarker(
      -1, -- add new marker
      1, -- regular region
      sec.name:gsub('"', "'"),
      math.max(0, prev_pos), -- start time (seconds)
      prev_pos + (num and denom and (sec.bars * 60.0 / bpm * num) or sec.bars),
      0x0099CCFF -- default color
    )

    reaper.AddProjectMarker(
      -1,
      true, -- is region
      sec.name:gsub('"', "'"),
      math.max(0, prev_pos),
      prev_pos + (num and denom and (sec.bars * 60.0 / bpm * num) or sec.bars),
      0x0099CCFF
    )

    if num and denom then
      local quarter_note_time = 60.0 / bpm
      prev_pos = prev_pos + (sec.bars * (quarter_note_time * num))
    else
      prev_pos = prev_pos + sec.bars
    end
  end
  reaper.Undo_OnStateChangeEx("midi_drums: Create sections", -1, -1)
end

-- ===== MIDI import =====

function M.import_midi(midi_path)
  local f = io.open(midi_path, "rb")
  if not f then return false, "MIDI file not found: " .. midi_path end
  f:close()
  reaper.Main_OnCommand(40073, 0) -- Media Item: Add MIDI item from file
  reaper.MediaItem_GetSetInfoString(nil, "D_FILENAME", midi_path)
  return true
end

-- ===== Timeline parsing & application (song-map mode) =====

function M.parse_timeline(content)
  local tempo_points = {}
  for time_s, bpm_s, num_s, denom_s in content:gmatch(
    '"time"%s*:%s*([%d.]+).*?"bpm"%s*:%s*(%d+).*?"num"%s*:%s*(%d+).*?"denom"%s*:%s*(%d+)'
  ) do
    tempo_points[#tempo_points + 1] = {
      time = tonumber(time_s) or 0,
      bpm = tonumber(bpm_s),
      num = tonumber(num_s),
      denom = tonumber(denom_s),
    }
  end

  local regions = {}
  for name, cg, start_t, end_t in content:gmatch(
    '"name"%s*:%s*"([^"]+)".*"color_group"%s*:%s*"([^"]+)".*"start_time"%s*:%s*([%d.]+).*?"end_time"%s*:%s*([%d.]+)'
  ) do
    regions[#regions + 1] = {
      name = name,
      color_group = cg,
      start_time = tonumber(start_t),
      end_time = tonumber(end_t),
    }
  end

  local color_groups = {}
  for name, r, g, b in content:gmatch(
    '"name"%s*:%s*"([^"]+)".*"r"%s*:%s*(%d+).*?"g"%s*:%s*(%d+).*?"b"%s*:%s*(%d+)'
  ) do
    color_groups[#color_groups + 1] = {
      name = name,
      r = tonumber(r), g = tonumber(g), b = tonumber(b),
    }
  end

  return tempo_points, regions, color_groups
end

function M.apply_timeline_to_reaper(tempo_points, regions, color_groups)
  -- Map color group names to RGB values for lookup
  local color_map = {}
  if color_groups then
    for _, cg in ipairs(color_groups) do
      color_map[cg.name] = { r = cg.r, g = cg.g, b = cg.b }
    end
  end

  -- First pass: remove all existing regions to avoid duplicates
  local num_markers = reaper.CountProjectMarkers(0)
  for i = num_markers - 1, 0, -1 do
    local is_reg, _, _, start_qn, end_qn, _, _ =
      reaper.EnumProjectMarkers3(0, i)
    if is_reg then
      reaper.DeleteProjectMarker(0, i, false)
    end
  end

  -- Second pass: place tempo markers and regions
  local time_to_qn_cache = {}
  for _, tp in ipairs(tempo_points or {}) do
    local qn = reaper.TimeMap_timeToQN(0, tp.time)
    reaper.SetTempoTimeSigMarker(-1, qn, tp.bpm, tp.num, tp.denom, 0)
  end

  -- Apply regions with colors
  for _, reg in ipairs(regions or {}) do
    local start_qn = reaper.TimeMap2_timeToQN(0, reg.start_time)
    local end_qn = reaper.TimeMap2_timeToQN(0, reg.end_time)
    local color_val = 0x0099CCFF -- default blue
    if reg.color_group and color_map[reg.color_group] then
      local cg = color_map[reg.color_group]
      color_val = bit32.bor(cg.r + (cg.g * 256) + (cg.b * 65536), 0xFF000000)
    end
    reaper.AddProjectMarker(-1, true, reg.name, start_qn, end_qn, color_val)
  end

  reaper.Undo_OnStateChangeEx("midi_drums: Apply song map timeline", -1, -1)
end

-- ===== CLI command builders (all use our midi-drums CLI contract) =====

function M.build_template_cmd(python_exe, genre, style, mapping, sidecar_path, midi_out, drummer)
  local parts = { python_exe, "-m midi_drums.api.cli", "generate" }
  parts[#parts + 1] = string.format("--genre %s", M.shell_escape(genre))
  parts[#parts + 1] = string.format("--style %s", M.shell_escape(style))
  parts[#parts + 1] = string.format("--sidecar %s", M.shell_escape(sidecar_path))
  parts[#parts + 1] = string.format("--output %s", M.shell_escape(midi_out))

  if mapping and mapping ~= "" then
    parts[#parts + 1] = string.format("--mapping %s", M.shell_escape(mapping))
  end
  if drummer and drummer ~= "" then
    parts[#parts + 1] = string.format("--drummer %s", M.shell_escape(drummer))
  end

  return table.concat(parts, " ")
end

function M.build_ai_cmd(python_exe, description, ai_tempo, midi_out, sidecar_path)
  local desc_escaped = description:gsub("'", "\\'")
  local parts = { python_exe, "-m midi_drums.api.cli", "prompt" }
  parts[#parts + 1] = string.format("' %s '", desc_escaped)
  parts[#parts + 1] = "--song"
  parts[#parts + 1] = string.format("--tempo %s", M.shell_escape(ai_tempo))
  parts[#parts + 1] = string.format("--write-sidecar %s", M.shell_escape(sidecar_path))
  parts[#parts + 1] = string.format("-o %s", M.shell_escape(midi_out))

  return table.concat(parts, " ")
end

function M.build_songmap_cmd(python_exe, genre, style, mapping, map_path, timeline_path, midi_out, drummer)
  local parts = { python_exe, "-m midi_drums.api.cli", "generate" }
  parts[#parts + 1] = string.format("--genre %s", M.shell_escape(genre))
  parts[#parts + 1] = string.format("--style %s", M.shell_escape(style))
  parts[#parts + 1] = string.format("--song-map %s", M.shell_escape(map_path))
  parts[#parts + 1] = string.format("--write-timeline %s", M.shell_escape(timeline_path))
  parts[#parts + 1] = string.format("-o %s", M.shell_escape(midi_out))

  if mapping and mapping ~= "" then
    parts[#parts + 1] = string.format("--mapping %s", M.shell_escape(mapping))
  end
  if drummer and drummer ~= "" then
    parts[#parts + 1] = string.format("--drummer %s", M.shell_escape(drummer))
  end

  return table.concat(parts, " ")
end

function M.build_riff_cmd(python_exe, params)
  -- Build the Python CLI command for riff-locked beat generation.
  -- Uses: midi-drums riff <audio_path> --genre X --style Y ...
  local parts = { python_exe, "-m midi_drums.api.cli", "riff" }
  parts[#parts + 1] = M.shell_escape(params.audio_path)

  if params.genre then      parts[#parts + 1] = string.format("--genre %s", M.shell_escape(params.genre)) end
  if params.style then      parts[#parts + 1] = string.format("--style %s", M.shell_escape(params.style)) end
  if params.drummer then    parts[#parts + 1] = string.format("--drummer %s", M.shell_escape(params.drummer)) end
  if params.bpm then        parts[#parts + 1] = string.format("--bpm %d", params.bpm) end
  if params.section then    parts[#parts + 1] = string.format("--section %s", M.shell_escape(params.section)) end
  if params.ts_num then     parts[#parts + 1] = string.format("--numerator %d", params.ts_num) end
  if params.ts_denom then   parts[#parts + 1] = string.format("--denominator %d", params.ts_denom) end
  if params.bars then       parts[#parts + 1] = string.format("--bars %d", params.bars) end
  if params.grid then       parts[#parts + 1] = string.format("--grid %s", M.shell_escape(params.grid)) end
  if params.lock_strength ~= nil then
    parts[#parts + 1] = string.format("--lock-strength %.1f", params.lock_strength) end
  if params.mapping then    parts[#parts + 1] = string.format("--mapping %s", M.shell_escape(params.mapping)) end
  if params.snare_mode then
    parts[#parts + 1] = string.format("--snare-mode %s", M.shell_escape(params.snare_mode)) end
  if params.snare_threshold ~= nil then
    parts[#parts + 1] = string.format("--snare-threshold %.2f", params.snare_threshold) end
  if params.offset_beats ~= nil then
    parts[#parts + 1] = string.format("--offset-beats %.4f", params.offset_beats) end
  if params.audio_offset ~= nil then
    parts[#parts + 1] = string.format("--audio-offset %.6f", params.audio_offset) end
  if params.audio_duration then
    parts[#parts + 1] = string.format("--audio-duration %.6f", params.audio_duration) end
  if params.midi_out then   parts[#parts + 1] = string.format("-o %s", M.shell_escape(params.midi_out)) end
  if params.sidecar_path then
    parts[#parts + 1] = string.format("--write-sidecar %s", M.shell_escape(params.sidecar_path)) end

  return table.concat(parts, " ")
end

-- ===== Riff job complete handler =====

function M.on_riff_complete(params)
  -- Import sidecar regions if available
  local f = io.open(params.sidecar_path, "rb")
  if f then
    local content = f:read("*a")
    f:close()
    local tempo, ts_num, ts_denom, secs = M.parse_sidecar(content)
    if tempo and secs then
      -- Create regions on top of existing timeline
      local bar_time = (60.0 / tempo) * ts_num
      for _, sec in ipairs(secs) do
        local color = 0x4A90D9FF -- blue-ish
        reaper.AddProjectMarker(-1, true, sec.name, params.region_start_time,
          params.region_start_time + (bar_time * sec.bars), color)
      end
    end
  end

  -- Import the riff MIDI onto a new track replacing the media item
  if params.midi_out then
    reaper.Main_OnCommand(40073, 0) -- Media Item: Add MIDI item from file
    reaper.MediaItem_GetSetInfoString(nil, "D_FILENAME", params.midi_out)

    -- Set time selection to the riff region for easy auditioning
    reaper.SetEditMarker2(0, "midi_drums: Riff Beat", params.region_start_time, 4.0, false)
  end
end

return M
