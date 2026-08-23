-- reaper/midi_drums_panel.lua
-- MIDI Drums: unified panel. Replaces create_song_sections.lua with a dockable
-- ReaImGui window featuring Song Sections / Riff-Lock Beat / Settings / Log tabs.

local script_path = ({reaper.get_action_context()}):match("^(.*[/\\])") or ""
package.path = package.path .. ";" .. script_path .. "midi_drums/?.lua"

local settings = dofile(script_path .. "midi_drums/settings.lua")
local job_runner = dofile(script_path .. "midi_drums/job_runner.lua")
local sections = dofile(script_path .. "midi_drums/sections.lua")
local riff_lock = dofile(script_path .. "midi_drums/riff_lock.lua")

-- ReaImGui guard — prompt user with setup instructions if missing
if not reaper.APIExists("ImGui_CreateContext") then
  reaper.ShowMessageBox(
    "This panel requires ReaImGui.\n\n"
    .. "To install:\n"
    .. "1. Extensions > ReaPack > Browse packages...\n"
    .. '2. Search for "ReaImGui"\n'
    .. '3. Right-click "ReaImGui: ReaScript binding for Dear ImGui" > Install\n'
    .. "4. Apply, then restart REAPER.",
    "ReaImGui Required", 0
  )
  return
end

local ctx = reaper.ImGui_CreateContext("midi_drums Panel")

-- Custom fonts (Segoe UI for body, Consolas for logs)
local font_sans = reaper.ImGui_CreateFont("Segoe UI", 14)
local font_mono = reaper.ImGui_CreateFont("Consolas", 13)
if font_sans then reaper.ImGui_Attach(ctx, font_sans) end
if font_mono then reaper.ImGui_Attach(ctx, font_mono) end

-- ===== Help popover system =====

-- Renders a "?" button that opens a tooltip when hovered/clicked.
local function draw_help_button(id, lines)
  if reaper.ImGui_IsItemClicked(0) then
    reaper.ImGui_OpenPopup(ctx, "help_" .. id)
  end
  if reaper.ImGui_BeginPopup(ctx, "help_" .. id) then
    for _, entry in ipairs(lines) do
      reaper.ImGui_TextColored(ctx, 0xa78bfaff, entry.title)
      reaper.ImGui_TextWrapped(ctx, entry.body)
      reaper.ImGui_Separator(ctx)
    end
    reaper.ImGui_EndPopup(ctx)
  end
end

-- ===== Song Sections tab =====

local ss_mode = 1 -- 1=REAPER, 2=Sidecar, 3=AI, 4=Song Map
local ss_genre = settings.get("default_genre")
local ss_style = settings.get("default_style")
local ss_mapping = settings.get("default_mapping")
local ss_drummer = ""
local ss_ai_description = "Epic rock drum solo with complex fills"
local ss_ai_tempo = settings.get("default_ai_tempo")
local ss_status = "Ready."

local SS_MODE_HELP = {
  { title = "REAPER", body = "Use REAPER's current tempo/time-sig and create regions from a default structure. Generates MIDI via Python template engine (~1-2s)." },
  { title = "Sidecar", body = "Read an existing midi_drums_sections.json sidecar file and create regions to match it. No subprocess launched." },
  { title = "AI", body = "Describe the song in plain text; AI composes → writes sidecar + MIDI (~20-45s). Requires API key in .env." },
  { title = "Song Map", body = "Read a song-map JSON (per-bar tempo/meter) and build a tempo-aware timeline with colored regions." },
}

local function draw_song_sections_tab()
  -- Mode selector with help button
  reaper.ImGui_Text(ctx, "Mode:")
  if reaper.ImGui_RadioButton(ctx, "REAPER", ss_mode == 1) then ss_mode = 1 end
  reaper.ImGui_SameLine(ctx)
  if reaper.ImGui_RadioButton(ctx, "Sidecar", ss_mode == 2) then ss_mode = 2 end
  reaper.ImGui_SameLine(ctx)
  if reaper.ImGui_RadioButton(ctx, "AI", ss_mode == 3) then ss_mode = 3 end
  reaper.ImGui_SameLine(ctx)
  if reaper.ImGui_RadioButton(ctx, "Song Map", ss_mode == 4) then ss_mode = 4 end
  draw_help_button("ss_mode", SS_MODE_HELP)

  reaper.ImGui_Separator(ctx)

  -- Mode-specific fields
  local changed
  if ss_mode == 3 then
    -- AI mode: large text input for description
    changed, ss_ai_description = reaper.ImGui_InputTextMultiline(
      ctx, "Description", ss_ai_description, -1, -1
    )
    reaper.ImGui_SameLine(ctx)
    if reaper.ImGui_Button(ctx, "(clear)") then ss_ai_description = "" end

    changed, ss_ai_tempo = reaper.ImGui_InputText(ctx, "Tempo (BPM)", ss_ai_tempo)
  else
    -- All other modes: genre/style/drummer/mapping fields
    changed, ss_genre = reaper.ImGui_InputText(ctx, "Genre", ss_genre)
    changed, ss_style = reaper.ImGui_InputText(ctx, "Style", ss_style)
    changed, ss_drummer = reaper.ImGui_InputText(ctx, "Drummer (opt.)", ss_drummer)
    changed, ss_mapping = reaper.ImGui_InputText(ctx, "Mapping", ss_mapping)

    -- Mode-specific help hints
    if ss_mode == 1 then
      reaper.ImGui_TextWrapped(ctx, "Uses REAPER's tempo/time-sig. Default structure: Intro(8), Verse(8), Chorus(8), Bridge(4), Outro(4).")
    elseif ss_mode == 2 then
      local proj = sections.get_project_dir()
      reaper.ImGui_TextWrapped(ctx, "Reads sidecar from: %s/midi_drums_sections.json", proj)
    elseif ss_mode == 4 then
      local proj = sections.get_project_dir()
      reaper.ImGui_TextWrapped(ctx, 'Prompts for song-map JSON path. Written by Python API (export_song_map_json).')
    end
  end

  reaper.ImGui_Separator(ctx)

  -- Generate button (disabled while a job is running)
  local disabled = job_runner.is_running()
  if disabled then reaper.ImGui_BeginDisabled(ctx) end
  if reaper.ImGui_Button(ctx, "Generate") then
    local python_exe = settings.resolve_python_exe()
    if not python_exe then
      ss_status = "Cancelled: no Python configured."
    else
      local sc_path = sections.get_project_dir() .. "/midi_drums_sections.json"
      local midi_out = sections.get_project_dir() .. "/midi_drums_song.mid"

      -- Save defaults for next run
      settings.set("default_genre", ss_genre)
      settings.set("default_style", ss_style)
      settings.set("default_mapping", ss_mapping)
      settings.set("default_ai_tempo", ss_ai_tempo)

      if ss_mode == 1 then
        -- REAPER mode: create regions from default structure, call Python template engine
        local ts_num, ts_denom = reaper.GetProjectTimeSignature2(0)
        local bpm = reaper.Master_GetTempo()

        local default_secs = {
          { name = "Intro", bars = 8 },
          { name = "Verse", bars = 16 },
          { name = "Chorus", bars = 16 },
          { name = "Bridge", bars = 8 },
          { name = "Outro", bars = 4 },
        }
        sections.create_regions_from_sections(default_secs, bpm, ts_num, ts_denom)

        local json = sections.sections_to_json(default_secs, bpm, ts_num, ts_denom)
        local f = io.open(sc_path, "w")
        if f then f:write(json); f:close() end

        local cmd = sections.build_template_cmd(
          python_exe, ss_genre, ss_style, ss_mapping, sc_path, midi_out, ss_drummer
        )
        job_runner.start(cmd, "Song Sections (REAPER)", function()
          sections.import_midi(midi_out)
          ss_status = "Done."
        end)
        ss_status = "Running..."

      elseif ss_mode == 2 then
        -- Sidecar mode: read existing sidecar, create regions from it
        local f = io.open(sc_path, "rb")
        if not f then
          ss_status = "Sidecar not found: " .. sc_path
        else
          local content = f:read("*a")
          f:close()
          local tempo, ts_num, ts_denom, secs = sections.parse_sidecar(content)
          if not tempo then
            ss_status = "Sidecar parse error: unknown format"
          else
            sections.create_regions_from_sections(secs, tempo, ts_num, ts_denom)
            ss_status = string.format("Created %d regions from sidecar.", #secs)
          end
        end

      elseif ss_mode == 3 then
        -- AI mode: generate song from natural language description
        if not ss_ai_description or ss_ai_description:gsub("%s+", "") == "" then
          ss_status = "Description cannot be empty."
        else
          local cmd = sections.build_ai_cmd(
            python_exe, ss_ai_description, ss_ai_tempo, midi_out, sc_path
          )
          job_runner.start(cmd, "Song Sections (AI)", function()
            local f = io.open(sc_path, "rb")
            if f then
              local content = f:read("*a")
              f:close()
              local tempo, ts_num, ts_denom, secs = sections.parse_sidecar(content)
              if tempo and secs then
                reaper.Undo_OnStateChangeEx("midi_drums: Clear regions", -1, -1)
                local num_markers = reaper.CountProjectMarkers(0)
                for i = num_markers - 1, 0, -1 do
                  local is_reg = reaper.EnumProjectMarkers3(0, i)
                  if is_reg then reaper.DeleteProjectMarker(0, i, false) end
                end
                sections.create_regions_from_sections(secs, tempo, ts_num, ts_denom)
              end
            end
            sections.import_midi(midi_out)
            ss_status = "Done."
          end)
          ss_status = "Running AI (20-45s)..."
        end

      elseif ss_mode == 4 then
        -- Song Map mode: read JSON, build timeline, call Python engine
        local map_path = sections.get_project_dir() .. "/midi_drums_song_map.json"
        local timeline_path = sections.get_project_dir() .. "/midi_drums_timeline.json"

        -- Prompt for song-map JSON path
        local ok, input = reaper.GetUserInputs(
          "Song Map", 1, "Song map JSON path,extrawidth=300", map_path
        )
        if not ok or input == "" then
          ss_status = "Cancelled."
          return
        end

        -- Verify file exists and try to parse it first (quick check)
        local f = io.open(input, "rb")
        if f then f:close() else
          ss_status = "File not found: " .. input
          return
        end

        local cmd = sections.build_songmap_cmd(
          python_exe, ss_genre, ss_style, ss_mapping, input, timeline_path, midi_out, ss_drummer
        )
        job_runner.start(cmd, "Song Sections (Song Map)", function()
          -- Read back the generated timeline JSON
          local f = io.open(timeline_path, "rb")
          if not f then
            ss_status = "Timeline file not found. Check Python output."
            return
          end
          local content = f:read("*a")
          f:close()

          local tempo_points, regions, color_groups = sections.parse_timeline(content)
          if tempo_points and regions then
            reaper.Undo_OnStateChangeEx("midi_drums: Clear timeline", -1, -1)
            -- Remove all existing markers/regions
            local num_markers = reaper.CountProjectMarkers(0)
            for i = num_markers - 1, 0, -1 do
              if reaper.EnumProjectMarkers3(0, i) then
                reaper.DeleteProjectMarker(0, i, false)
              end
            end
            sections.apply_timeline_to_reaper(tempo_points, regions, color_groups)
          else
            ss_status = "Timeline parse failed. Check JSON format."
          end

          sections.import_midi(midi_out)
          ss_status = "Done."
        end)
        ss_status = "Running song map..."
      end
    end
  end
  if disabled then reaper.ImGui_EndDisabled(ctx) end

  -- Status display
  local status_color
  if string.find(ss_status, "Done") then
    status_color = 0x4ade80ff -- green
  elseif string.find(ss_status, "Error") or string.find(ss_status, "Cancelled") then
    status_color = 0xfb7185ff -- red
  else
    status_color = 0x38bdf8ff -- blue/running
  end
  reaper.ImGui_TextColored(ctx, status_color, ss_status)

  if job_runner.is_running() then
    reaper.SameLine(ctx)
    reaper.ImGui_Text(ctx, string.format(" (%.1fs)", job_runner.elapsed_seconds()))
  end
end

-- ===== Riff-Lock Beat tab =====

local rl_genre = settings.get("default_genre")
local rl_style = settings.get("default_style")
local rl_drummer = ""
local rl_section = "verse"
local rl_mapping = settings.get("default_mapping")
local rl_grid = "16th"
local rl_lock_strength = 1.0
local rl_snare_mode = 2 -- 1=Off, 2=Reinforce, 3=Stab
local rl_snare_threshold = 0.85
local rl_status = "Select a riff item first."

local RL_SNARE_HELP = {
  { title = "Off", body = "Snare unaffected by riff — comes purely from genre plugin/drummer style." },
  { title = "Reinforce", body = "Boosts velocity on existing snare beats near strong riff accents." },
  { title = "Stab", body = "Inserts a unison snare hit at very strong accents where kick was locked but no snare nearby." },
}

local rl_has_item = false

local function draw_riff_lock_tab()
  -- Check if any media item is selected (read fresh each frame)
  local item_count = reaper.CountSelectedMediaItems(0)
  local first_item = item_count > 0 and reaper.GetSelectedMediaItem(0, 0) or nil

  if not first_item then
    rl_status = "Select a riff media item first."
    reaper.ImGui_TextColored(ctx, 0xfb7185ff, "⚠ No riff selected")
    rl_has_item = false
  else
    rl_has_item = true
    local name_buf = {}
    reaper.GetSetMediaItemStr(first_item, "D_NAME", name_buf)
    reaper.ImGui_TextColored(ctx, 0x4ade80ff, string.format("✓ %s selected", item_count > 1 and string.format("%d items (first used)", item_count) or "item selected"))
  end

  reaper.ImGui_Separator(ctx)

  -- Riff controls
  local changed
  changed, rl_genre = reaper.ImGui_InputText(ctx, "Genre", rl_genre)
  changed, rl_style = reaper.ImGui_InputText(ctx, "Style", rl_style)
  changed, rl_drummer = reaper.ImGui_InputText(ctx, "Drummer (opt.)", rl_drummer)
  changed, rl_section = reaper.ImGui_InputText(ctx, "Section", rl_section)
  changed, rl_mapping = reaper.ImGui_InputText(ctx, "Mapping", rl_mapping)
  changed, rl_grid = reaper.ImGui_InputText(ctx, "Grid (1/8,16th...)", rl_grid)

  -- Lock strength slider
  local ls_new, _ = reaper.ImGui_SliderDouble(ctx, "Lock Strength", rl_lock_strength, 0.0, 1.0)
  if ls_new then rl_lock_strength = ls_new end

  -- Snare reaction mode
  reaper.ImGui_Text(ctx, "Snare Reaction:")
  if reaper.ImGui_RadioButton(ctx, "Off", rl_snare_mode == 1) then rl_snare_mode = 1 end
  reaper.ImGui_SameLine(ctx)
  if reaper.ImGui_RadioButton(ctx, "Reinforce", rl_snare_mode == 2) then rl_snare_mode = 2 end
  reaper.ImGui_SameLine(ctx)
  if reaper.ImGui_RadioButton(ctx, "Stab", rl_snare_mode == 3) then rl_snare_mode = 3 end
  draw_help_button("rl_snare", RL_SNARE_HELP)

  -- Stab threshold (only for Stab mode)
  if rl_snare_mode == 3 then
    local st_new, _ = reaper.ImGui_SliderDouble(ctx, "Stab Threshold", rl_snare_threshold, 0.0, 1.0)
    if st_new then rl_snare_threshold = st_new end
  end

  -- Generate button (disabled while running or no riff selected)
  local disabled = job_runner.is_running() or not rl_has_item
  if disabled then reaper.ImGui_BeginDisabled(ctx) end
  if reaper.ImGui_Button(ctx, "Generate Riff Beat") then
    local python_exe = settings.resolve_python_exe()
    if not python_exe then
      rl_status = "Cancelled: no Python configured."
    else
      -- Compute bar alignment for the selected item
      local offset_beats, bar_start_qn, bar_end_qn, ts_num, ts_denom, bpm =
        riff_lock.compute_bar_alignment(first_item)

      -- Render audio from selection to temp WAV
      local take = reaper.GetActiveTake(first_item)
      if not take then
        rl_status = "Selected item has no active take."
      else
        local audio_path, audio_offset, audio_duration, err =
          riff_lock.resolve_audio_source(first_item, take, bar_start_qn, bar_end_qn)

        if not audio_path then
          rl_status = "Audio error: " .. (err or "could not render")
        else
          -- Save defaults
          settings.set("default_genre", rl_genre)
          settings.set("default_style", rl_style)
          settings.set("default_mapping", rl_mapping)

          local sc_path = sections.get_project_dir() .. "/midi_drums_sections.json"
          local midi_out = sections.get_project_dir() .. "/midi_drums_riff.mid"
          local snare_mode_str = "off"
          if rl_snare_mode == 2 then snare_mode_str = "reinforce"
          elseif rl_snare_mode == 3 then snare_mode_str = "stab" end

          local cmd = riff_lock.build_cmd(python_exe, {
            audio_path = audio_path,
            audio_offset = audio_offset,
            audio_duration = audio_duration,
            genre = rl_genre,
            style = rl_style,
            drummer = rl_drummer,
            bpm = bpm,
            section = rl_section,
            ts_num = ts_num,
            ts_denom = ts_denom,
            bars = 4,
            grid = rl_grid,
            lock_strength = rl_lock_strength,
            mapping = rl_mapping,
            snare_mode = snare_mode_str,
            snare_threshold = rl_snare_threshold,
            offset_beats = offset_beats,
            midi_out = midi_out,
            sidecar_path = sc_path,
          })

          local region_start_time = reaper.TimeMap2_QNToTime(0, bar_start_qn)

          job_runner.start(cmd, "Riff-Lock Beat", function()
            riff_lock.on_job_complete({
              sidecar_path = sc_path,
              midi_out = midi_out,
              region_start_time = region_start_time,
            })
            rl_status = "Done. Check Log tab for details."
          end)
          rl_status = "Running riff lock..."
        end
      end
    end
  end
  if disabled then reaper.ImGui_EndDisabled(ctx) end

  -- Status
  local status_color = string.find(rl_status, "Done") and 0x4ade80ff or
    (string.find(rl_status, "Error") and 0xfb7185ff or 0x38bdf8ff)
  reaper.ImGui_TextColored(ctx, status_color, rl_status)
end

-- ===== Settings tab =====

local function settings_field(label, key)
  local value = settings.get(key)
  local changed, new_value = reaper.ImGui_InputText(ctx, label, value)
  if changed then
    settings.set(key, new_value)
  end
end

local function draw_settings_tab()
  reaper.ImGui_Text(ctx, "Python interpreter")
  settings_field("Python exe path", "python_exe")

  -- Test button for Python path
  if reaper.ImGui_Button(ctx, "(test)") then
    local exe = settings.get("python_exe")
    if exe == "" or exe:match("^%s*$") then
      reaper.ShowMessageBox("No Python path configured.", "Settings", 0)
    elseif io.open(exe, "rb") then
      reaper.ShowMessageBox("Path OK:\n" .. exe, "Settings", 0)
    else
      reaper.ShowMessageBox("Path NOT FOUND.\nUpdate the field above.", "Settings", 0)
    end
  end
  reaper.ImGui_SameLine(ctx)
  local ok = io.open(settings.get("python_exe") or "", "rb")
  if ok then
    reaper.ImGui_TextColored(ctx, 0x4ade80ff, "✓")
    ok:close()
  else
    reaper.ImGui_TextColored(ctx, 0xfb7185ff, "✗")
  end

  reaper.ImGui_Separator(ctx)
  reaper.ImGui_Text(ctx, "Defaults (used for new generations)")
  settings_field("Default genre", "default_genre")
  settings_field("Default style", "default_style")
  settings_field("Default mapping", "default_mapping")
  settings_field("Default AI tempo", "default_ai_tempo")
  settings_field("Sidecar path override", "sidecar_path_override")

  reaper.ImGui_Separator(ctx)
  reaper.ImGui_TextWrapped(ctx,
    "midi_drums Panel v2 — unified REAPER integration.\n"
    .. "Generates drum MIDI via our midi-drums CLI and imports into this project.\n\n"
    .. "Requires ReaImGui (Extensions > ReaPack) + midi_drums Python package."
  )

  -- Show current version info
  reaper.ImGui_Separator(ctx)
  reaper.ImGui_TextColored(ctx, 0xa78bfaff, string.format("Panel built for our fork — CLI matches %s contract.", "midi-drums"))
end

-- ===== Log tab =====

local STATUS_COLORS = {
  idle = 0x778ca6ff,
  running = 0x38bdf8ff,
  done = 0x4ade80ff,
  error = 0xfb7185ff,
}

local function draw_log_tab()
  local st = job_runner.state

  -- Job info line with elapsed time
  reaper.ImGui_Text(ctx, "Job: " .. (st.job_label or "(none)"))
  reaper.ImGui_SameLine(ctx)
  if job_runner.is_running() then
    reaper.ImGui_Text(ctx, string.format("(%.1fs)", job_runner.elapsed_seconds()))
  end
  reaper.ImGui_SameLine(ctx)
  local col = STATUS_COLORS[st.status] or STATUS_COLORS.idle
  reaper.ImGui_TextColored(ctx, col, st.status:upper())

  -- Auto-refresh button
  if reaper.ImGui_Button(ctx, "Refresh") then
    job_runner.poll() -- force poll in case defer() missed a frame
  end

  reaper.ImGui_Separator(ctx)

  -- Log box (monospace font)
  if font_mono then reaper.ImGui_PushFont(ctx, font_mono) end
  if reaper.ImGui_BeginChild(ctx, "log_box", 0, 300) then
    if #st.log_lines == 0 then
      reaper.ImGui_TextDisabled(ctx, "No job run yet.\nRun a generation and logs will appear here in real time.")
    else
      for _, line in ipairs(st.log_lines) do
        -- Colorize: green for "Done", red for "Error" or "Traceback"
        local col
        if line:find("Done") or line:find("output:") then col = 0x4ade80ff
        elseif line:find("Error") or line:find("traceback") or line:find("Failed") then col = 0xfb7185ff
        elseif line:find("%[%.%d+s%)") then col = 0x38bdf8ff
        else col = 0xffffff -- white for normal output
        end
        reaper.ImGui_TextColored(ctx, col, line)
      end
      if job_runner.is_running() then
        reaper.ImGui_SetScrollHereY(ctx, 1.0) -- auto-scroll to bottom
      end
    end
    reaper.ImGui_EndChild(ctx)
  end
  if font_mono then reaper.ImGui_PopFont(ctx) end

  -- Clear button
  if reaper.ImGui_Button(ctx, "Clear Log") then
    st.log_lines = {}
    st.status = M.STATUS.IDLE
    st.job_label = nil
    st.exit_code = nil
  end
end

-- ===== Main panel loop =====

local function loop()
  -- Poll job runner (check for subprocess completion)
  job_runner.poll()

  local visible, open = reaper.ImGui_Begin(ctx, "midi_drums Panel", true)
  if not visible then
    reaper.ImGui_End(ctx)
    return
  end

  if font_sans then reaper.ImGui_PushFont(ctx, font_sans) end

  -- Tabs bar
  if reaper.ImGui_BeginTabBar(ctx, "midi_drums_tabs") then
    if reaper.ImGui_BeginTabItem(ctx, "Song Sections") then
      draw_song_sections_tab()
      reaper.ImGui_EndTabItem(ctx)
    end
    if reaper.ImGui_BeginTabItem(ctx, "Riff-Lock Beat") then
      draw_riff_lock_tab()
      reaper.ImGui_EndTabItem(ctx)
    end
    if reaper.ImGui_BeginTabItem(ctx, "Settings") then
      draw_settings_tab()
      reaper.ImGui_EndTabItem(ctx)
    end
    if reaper.ImGui_BeginTabItem(ctx, "Log") then
      draw_log_tab()
      reaper.ImGui_EndTabItem(ctx)
    end
    reaper.ImGui_EndTabBar(ctx)
  end

  if font_sans then reaper.ImGui_PopFont(ctx) end

  reaper.ImGui_End(ctx)
end

-- Register for automatic execution (REAPER will call loop() each frame)
reaper.atexit(function()
  reaper.ImGui_DestroyContext(ctx)
end)

-- Main loop function that REAPER calls via a timer or defer
local function main_loop()
  loop()
end

return {
  name = "midi_drums Panel",
  version = "2.0.0",
  loop = main_loop,
}
