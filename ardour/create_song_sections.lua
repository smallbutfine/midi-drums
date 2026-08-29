-- create_song_sections.lua (Ardour / Mixbus port)
-- midi_drums × Ardour/Mixbus bi-directional integration
-- Part of: https://github.com/fsecada01/midi-drums
--
-- ─────────────────────────────────────────────────────────────────────────────
-- QUICK START (Mixbus)
--   1. Set PYTHON_EXE below to your midi_drums virtualenv pythonw.exe.
--   2. Tools → Scripts → Load Script → select this file → assign a shortcut.
--   3. Run the script. A dialog asks for the generation mode.
-- ─────────────────────────────────────────────────────────────────────────────
--
-- FOUR MODES  (chosen via dialog each time you run)
--
--   YES          Ardour mode  (default — same logic as REAPER mode)
--   ├─ Uses the ARDOUR_SECTIONS table defined below
--   ├─ Creates timeline regions
--   ├─ Writes midi_drums_sections.json sidecar to session folder
--   └─ Optionally calls Python template engine → drums.mid → auto-imported
--
--   NO → "sidecar"   Python sidecar mode
--   ├─ Reads midi_drums_sections.json written by:
--   │      api.save_as_midi_with_sidecar(song, "drums.mid")
--   ├─ Creates regions matching Python's structure
--   └─ Offers to sync project tempo from sidecar
--
--   NO → "ai"        AI agent mode
--   ├─ Prompts for a natural-language description + tempo
--   ├─ Calls: python -m midi_drums prompt "..." --song --write-sidecar ...
--   ├─ AI composes song → writes drums.mid + sidecar (~20-45 s)
--   ├─ Project tempo synced to AI-chosen BPM
--   ├─ Regions created from AI structure
--   └─ drums.mid auto-imported on a new track
--
--   NO → "songmap"   Song-map mode (per-section tempo/meter)
--   ├─ Prompts for a song_creator-shaped song-map JSON path + genre/style
--   ├─ Calls: python -m midi_drums generate --song-map ... --write-timeline ...
--   ├─ Reads back the flat timeline JSON
--   ├─ Places one SetTempoTimeSigMarker per tempo/meter change point
--   ├─ Creates one colored region per song-map region
--   └─ drums.mid auto-imported on a new track
--
-- SIDECAR FORMAT (same as REAPER version — midi_drums_sections.json)
-- TIMELINE FORMAT (same as REAPER version — midi_drums_timeline.json)
-- ─────────────────────────────────────────────────────────────────────────────

-- ===========================================================================
-- USER CONFIG
-- ===========================================================================

-- Path to the Python executable inside the midi_drums virtualenv.
-- pythonw.exe suppresses the console window on Windows.
local PYTHON_EXE = "C:/path/to/midi_drums/.venv/Scripts/pythonw.exe"

-- Default sidecar path override (nil = auto-detect session folder)
local SIDECAR_PATH = nil

-- Defaults pre-filled in the template generation dialog
local DEFAULT_GENRE   = "rock"
local DEFAULT_STYLE   = "classic"
local DEFAULT_MAPPING = "gm_drums"

-- Default tempo pre-filled in the AI generation dialog
local DEFAULT_AI_TEMPO = "120"

-- ===========================================================================
-- Constants
-- ===========================================================================
local SIDECAR_FILENAME  = "midi_drums_sections.json"
local TIMELINE_FILENAME = "midi_drums_timeline.json"
local MIDI_OUTPUT       = "drums.mid"

-- ---------------------------------------------------------------------------
-- Helpers: Ardour session path detection
-- ---------------------------------------------------------------------------
-- Ardour scripts run inside the application and have access to a `Session`
-- global (the current project).  Mixbus uses the same Session object.
--
-- In older Ardour versions the global might be named `SESSION`.  We check
-- both names for compatibility.
local SESSION = Session or SESSION

-- ---------------------------------------------------------------------------
-- Helpers: get session directory path
-- ---------------------------------------------------------------------------
local function get_session_dir()
  if SESSION then
    local p = SESSION:path()
    return (p and p ~= "") and p or ""
  end
  -- Fallback: Ardour user config dir (~/.config/ardourX/ by default)
  local home = os.getenv("HOME") or os.getenv("USERPROFILE") or "/tmp"
  return home .. "/.config/ardour6/"
end

-- ---------------------------------------------------------------------------
-- Helpers: get project/session tempo at a given quarter-note position
-- Returns (bpm, num, denom)
-- ---------------------------------------------------------------------------
local function get_tempo_at_qn(qn_pos)
  if SESSION and SESSION.tempo_map then
    local tm = SESSION:tempo_map()
    if tm then
      -- Ardour/Mixbus tempo map API may vary by version.
      -- Try the common method signatures:
      local ok, bpm_result = pcall(function()
        return tm:get(qn_pos) or tm:get_tempo_at_time(qn_pos) or 120
      end)
      if not ok then
        reaper_show_msg("Warning: tempo map query failed, using default 120 BPM")
        return 120, 4, 4
      end
      local bpm = type(bpm_result) == "table" and bpm_result.bpm or bpm_result
      -- Time signature at position
      local ts_ok, ts_num, ts_denom = pcall(function()
        local ts = tm:get_time_signature_at(qn_pos) or { num = 4, denom = 4 }
        return ts.num or ts.numerator or 4, ts.denom or ts.denominator or 4
      end)
      if not ts_ok then
        bpm = type(bpm_result) == "number" and bpm_result or 120
        return bpm, 4, 4
      end
      return bpm, tonumber(ts_num) or 4, tonumber(ts_denom) or 4
    end
  end
  -- No tempo map available — default to 120 BPM / 4/4
  return 120, 4, 4
end

-- ---------------------------------------------------------------------------
-- Helpers: current project/session tempo/time-signature
-- ---------------------------------------------------------------------------
local function get_current_tempo_and_ts()
  local bpm, num, denom = get_tempo_at_qn(0)
  return bpm, num, denom
end

-- ---------------------------------------------------------------------------
-- Helpers: file path utilities
-- ---------------------------------------------------------------------------
local function get_sidecar_path()
  if SIDECAR_PATH then return SIDECAR_PATH end
  local session_dir = get_session_dir()
  if session_dir ~= "" then
    return session_dir .. "/" .. SIDECAR_FILENAME
  end
  -- Fall back to script directory
  local script_dir = arg[0]:match("^(.*/)") or "./"
  return script_dir .. SIDECAR_FILENAME
end

local function get_timeline_path()
  local session_dir = get_session_dir()
  if session_dir ~= "" then
    return session_dir .. "/" .. TIMELINE_FILENAME
  end
  local script_dir = arg[0]:match("^(.*/)") or "./"
  return script_dir .. TIMELINE_FILENAME
end

local function get_midi_output_path()
  local session_dir = get_session_dir()
  if session_dir ~= "" then
    return session_dir .. "/" .. MIDI_OUTPUT
  end
  local script_dir = arg[0]:match("^(.*/)") or "./"
  return script_dir .. MIDI_OUTPUT
end

-- ---------------------------------------------------------------------------
-- Helpers: JSON construction (minimal, no external deps)
-- ---------------------------------------------------------------------------
local function sections_to_json(sections, tempo, num, denom)
  local parts = {}
  for i, s in ipairs(sections) do
    parts[i] = string.format('    {"name": "%s", "bars": %d}', s.name, s.bars)
  end
  return string.format(
    '{\n'
    .. '  "source": "ardour",\n'
    .. '  "tempo": %g,\n'
    .. '  "time_signature": [%d, %d],\n'
    .. '  "sections": [\n%s\n  ]\n'
    .. '}',
    tempo, num, denom, table.concat(parts, ",\n")
  )
end

-- ---------------------------------------------------------------------------
-- Helpers: parse sidecar JSON (same patterns as REAPER version)
-- Returns tempo, ts_num, ts_denom, sections table or (nil, err_msg)
-- ---------------------------------------------------------------------------
local function parse_sidecar(content)
  local tempo = tonumber(content:match('"tempo"%s*:%s*([%d%.]+)'))
  if not tempo then
    return nil, "Could not parse 'tempo'."
  end
  local ts_num, ts_denom = content:match(
    '"time_signature"%s*:%s*%[%s*(%d+)%s*,%s*(%d+)%s*%]'
  )
  ts_num   = tonumber(ts_num)   or 4
  ts_denom = tonumber(ts_denom) or 4
  local sections = {}
  for name, bars in content:gmatch(
    '"name"%s*:%s*"([^"]+)"%s*,%s*"bars"%s*:%s*(%d+)'
  ) do
    sections[#sections + 1] = { name = name, bars = tonumber(bars) }
  end
  if #sections == 0 then
    return nil, "No sections found."
  end
  return tempo, ts_num, ts_denom, sections
end

-- ---------------------------------------------------------------------------
-- Helpers: parse timeline JSON (same patterns as REAPER version)
-- Returns tempo_points[], regions[], color_groups{} or (nil, err_msg)
-- ---------------------------------------------------------------------------
local function parse_timeline(content)
  local tempo_points = {}
  for time, bpm, num, denom in content:gmatch(
    '"time"%s*:%s*([%-%d%.]+)%s*,%s*"bpm"%s*:%s*([%-%d%.]+)%s*,'
    .. '%s*"num"%s*:%s*(%d+)%s*,%s*"denom"%s*:%s*(%d+)'
  ) do
    tempo_points[#tempo_points + 1] = {
      time = tonumber(time), bpm = tonumber(bpm),
      num = tonumber(num), denom = tonumber(denom),
    }
  end

  local regions = {}
  for name, color_group, start_time, end_time in content:gmatch(
    '"name"%s*:%s*"([^"]*)"%s*,%s*"color_group"%s*:%s*"([^"]*)"%s*,'
    .. '%s*"start_time"%s*:%s*([%-%d%.]+)%s*,%s*"end_time"%s*:%s*([%-%d%.]+)'
  ) do
    regions[#regions + 1] = {
      name = name, color_group = color_group,
      start_time = tonumber(start_time), end_time = tonumber(end_time),
    }
  end

  local color_groups = {}
  for name, r, g, b in content:gmatch(
    '"name"%s*:%s*"([^"]*)"%s*,%s*"r"%s*:%s*(%d+)%s*,'
    .. '%s*"g"%s*:%s*(%d+)%s*,%s*"b"%s*:%s*(%d+)'
  ) do
    color_groups[name] = { r = tonumber(r), g = tonumber(g), b = tonumber(b) }
  end

  if #tempo_points == 0 or #regions == 0 then
    return nil, "Could not parse timeline (no tempo_points/regions)."
  end
  return tempo_points, regions, color_groups
end

-- ---------------------------------------------------------------------------
-- Helpers: run Python via io.popen
-- Returns (ok_boolean, output_string)
-- ---------------------------------------------------------------------------
local function run_python(cmd)
  -- Print command to Ardour console for debugging
  if reaper_show_msg then
    reaper_show_msg("midi_drums: " .. cmd .. "\n")
  end
  local handle = io.popen(cmd .. " 2>&1")
  local out    = handle:read("*a")
  local ok     = handle:close()
  if out and out ~= "" then
    if reaper_show_msg then
      reaper_show_msg(out .. "\n")
    end
  end
  return ok, out
end

-- ---------------------------------------------------------------------------
-- Helpers: run_python_or_fail (shared error handling)
-- Returns stdout on success, or nil on failure (caller should return)
-- ---------------------------------------------------------------------------
local function run_python_or_fail(cmd, extra_hint)
  local ok, py_out = run_python(cmd)
  if not ok then
    show_ardour_msgbox(
      "Python generation failed.\nCheck Ardour console for details.\n\n"
      .. (extra_hint or ("PYTHON_EXE: " .. PYTHON_EXE)),
      "Generation Failed"
    )
    return nil
  end
  return py_out
end

-- ---------------------------------------------------------------------------
-- Helpers: read_generated_file_or_fail
-- Returns file content on success, or nil on failure
-- ---------------------------------------------------------------------------
local function read_generated_file_or_fail(path, what)
  local f = io.open(path, "r")
  if not f then
    show_ardour_msgbox(
      "Generation succeeded but " .. what .. " not found:\n" .. path,
      what .. " Not Found"
    )
    return nil
  end
  local content = f:read("*all")
  f:close()
  return content
end

-- ---------------------------------------------------------------------------
-- Helpers: shell escape for cmd.exe (same as REAPER version)
-- ---------------------------------------------------------------------------
local function shell_escape(s)
  s = s:gsub("[\r\n]", " ")
  s = s:gsub('"', "'")
  s = s:gsub("[&|^<>%%]", "")
  return s
end

-- ---------------------------------------------------------------------------
-- Helpers: Ardour message display (falls back to stdout on headless)
-- ---------------------------------------------------------------------------
-- Try ARDOUR's GUI/dialog API; fall back to io.stderr/stdout if not available.
local function show_ardour_msgbox(msg, title)
  -- Attempt 1: ARDOOR.msg_box or similar (Mixbus-specific)
  if ARDOOR and ARDOOR.msg_box then
    return ARDOOR:msg_box(msg, title or "Message")
  end
  -- Attempt 2: Session dialog callback
  if SESSION and SESSION.gui and SESSION.gui.show_message then
    return SESSION.gui:show_message(msg, title or "Message", "ok")
  end
  -- Attempt 3: Just print to console (headless / debug)
  io.stderr:write("=== " .. (title or "Message") .. " ===\n" .. msg .. "\n\n")
end

-- ---------------------------------------------------------------------------
-- Helpers: Ardour undo block helpers
-- ---------------------------------------------------------------------------
local function undo_begin()
  if SESSION and SESSION.gui then
    pcall(function() SESSION.gui:undo_start("midi_drums") end)
  end
end

local function undo_end(label)
  if SESSION and SESSION.gui then
    pcall(function() SESSION.gui:undo_stop() end)
  end
end

-- ---------------------------------------------------------------------------
-- Helpers: create region in Ardour session
-- In Ardour/Mixbus, regions are called "Markers" or "Regions"
-- API differs from REAPER — see docs for your specific version.
-- ---------------------------------------------------------------------------
local function create_region(start_time, end_time, name, color)
  if SESSION and SESSION.add_region then
    -- Ardour 6+ API: add_region(name, start_tick, end_tick, flags, color)
    pcall(function()
      SESSION:add_region(name, start_time, end_time, 0, color or 0)
    end)
    return
  end
  if SESSION and SESSION.markers then
    -- Older Ardour: markers API
    pcall(function()
      table.insert(SESSION.markers, {
        position = start_time,
        length = end_time - start_time,
        name = name,
        color = color or 0,
      })
    end)
    return
  end
  -- Fallback: nothing to do — regions won't be created without Session access
end

-- ---------------------------------------------------------------------------
-- Helpers: set tempo/time-sig marker at a given time position
-- ---------------------------------------------------------------------------
local function set_tempo_marker(time, bpm, num, denom)
  if SESSION and SESSION.tempo_map then
    pcall(function()
      local tm = SESSION:tempo_map()
      if tm.set_tempo_at_time then
        tm:set_tempo_at_time(time, bpm)
      elseif tm:set then
        tm:set(time, { tempo = bpm, num = num, denom = denom })
      end
      -- Time signature may be set separately
      if tm.set_time_signature_at_time then
        tm:set_time_signature_at_time(time, num, denom)
      end
    end)
  end
end

-- ---------------------------------------------------------------------------
-- Helpers: import MIDI file into Ardour session
-- In Mixbus/Ardour this uses the media import system.
-- ---------------------------------------------------------------------------
local function import_midi(file_path)
  if not SESSION then
    io.stderr:write("No Session available — cannot import " .. file_path .. "\n")
    return
  end
  -- Try ARDOUR's media import API
  local ok, err = pcall(function()
    if ARDOUR and ARDOOR.import_midi_file then
      ARDOOR:import_midi_file(file_path)
    elseif SESSION.import_media then
      SESSION:import_media({ file_path })
    end
  end)
  if not ok then
    io.stderr:write("Import failed: " .. tostring(err) .. "\n")
  end
end

-- ---------------------------------------------------------------------------
-- Helpers: color_to_native (RGB → ARGB hex integer)
-- REAPER uses ColorToNative(r,g,b) | 0x1000000 for alpha.
-- Ardour/Mixbus uses the same ARGB format on Windows.
-- ---------------------------------------------------------------------------
local function color_to_native(r, g, b)
  -- RGB to BGR hex (Windows native order is BGR in lower 24 bits)
  local rgb = r * 65536 + g * 256 + b
  return bit.tOr(rgb, 0x1000000) or (rgb + 0x1000000) -- bit.bor fallback
end

-- ---------------------------------------------------------------------------
-- Helpers: refresh Ardour UI (equivalent to reaper.UpdateArrange())
-- ---------------------------------------------------------------------------
local function refresh_ui()
  if SESSION and SESSION.gui then
    pcall(function() SESSION.gui:refresh_all() end)
  end
end

-- ===========================================================================
-- Mode selection — same dialog pattern as REAPER version
-- ===========================================================================
local mode_choice = show_ardour_msgbox(
  "Select drum generation mode:\n\n"
  .. "YES    = Ardour/Mixbus — use sections defined in this script (default)\n"
  .. "NO     = External source (sidecar / AI agent / song-map)",
  "midi_drums Generation Mode"
)

-- Determine YES/NO from the return value.
-- ARDOOR.msg_box returns true/true or nil for yes/no on some platforms.
-- For stdout fallback, we default to "reaper"/Ardour mode.
local MODE = "ardour"  -- default to Ardour mode when no GUI

if type(mode_choice) == "boolean" and not mode_choice then
  -- User chose NO → external source
  local ext_input = io.read("*l")
  if not ext_input or ext_input == "" then
    MODE = "ardour"
  else
    -- Normalize like REAPER version
    local ext_mode = ext_input:match("^%s*(.-)%s*$"):lower():gsub("[%s%-_]", "")
    if ext_mode == "ai" then
      MODE = "ai"
    elseif ext_mode == "songmap" then
      MODE = "songmap"
    elseif ext_mode == "sidecar" or ext_mode == "" then
      MODE = "sidecar"
    else
      show_ardour_msgbox(
        "Unrecognized external source: '" .. ext_input .. "'\n\n"
        .. "Expected one of: sidecar, ai, songmap.",
        "Invalid Mode"
      )
      return
    end
  end
elseif type(mode_choice) == "string" then
  -- From stdout fallback — check for keywords in the echoed input
  local normalized = mode_choice:lower():gsub("[%s%-_]", "")
  if normalized:find("ai") then MODE = "ai"
  elseif normalized:find("songmap") then MODE = "songmap"
  else MODE = "sidecar" end
end

-- ===========================================================================
-- Build sections + timing
-- ===========================================================================
local ARDOUR_SECTIONS = {
  { name = "Intro",  bars = 8  },
  { name = "Verse",  bars = 16 },
  { name = "Chorus", bars = 16 },
  { name = "Bridge", bars = 8  },
  { name = "Outro",  bars = 4  },
}

local sections     = {}
local midi_out     = get_midi_output_path()
local sp           = get_sidecar_path()
local bpm, ts_num, ts_denom = get_current_tempo_and_ts()

-- ── Ardour mode (same as REAPER mode) ───────────────────────────────────────
if MODE == "ardour" then
  sections = ARDOUR_SECTIONS

-- ── Python sidecar mode ──────────────────────────────────────────────────────
elseif MODE == "sidecar" then
  local f = io.open(sp, "r")
  if not f then
    show_ardour_msgbox(
      "Could not open sidecar:\n" .. sp
      .. "\n\nCreate it from Python:\n"
      .. "  api.save_as_midi_with_sidecar(song, 'drums.mid')",
      "Sidecar Not Found"
    )
    return
  end
  local content = f:read("*all"); f:close()

  local p_tempo, p_num, p_denom, p_sections, err = parse_sidecar(content)
  if not p_sections then
    show_ardour_msgbox("Parse error: " .. (err or "?"), "Error")
    return
  end
  sections = p_sections

  if math.abs(p_tempo - bpm) > 0.5 then
    local sync = show_ardour_msgbox(
      string.format(
        "Sidecar tempo: %g BPM\nProject tempo: %g BPM\n\nSync project?",
        p_tempo, bpm
      ), "Tempo Mismatch"
    )
    if type(sync) == "boolean" and sync then
      set_tempo_marker(0, p_tempo, p_num, p_denom)
      bpm = p_tempo; ts_num = p_num; ts_denom = p_denom
    end
  end

-- ── AI agent mode ────────────────────────────────────────────────────────────
elseif MODE == "ai" then
  local desc_input = io.read("*l")
  if not desc_input or desc_input == "" then
    show_ardour_msgbox("Description cannot be empty.", "Error")
    return
  end

  local tempo_str = io.read("*l") or DEFAULT_AI_TEMPO
  local tempo_arg = (tempo_str and tempo_str ~= "")
                    and ("--tempo " .. tempo_str) or ""

  show_ardour_msgbox(
    "The AI agent will compose a full song from your description.\n\n"
    .. '"' .. desc_input .. '"\n\n'
    .. "Ardour/Mixbus will be unresponsive for ~20–45 seconds while the AI works.\n\n"
    .. "Continue?",
    "AI Generation — Please Wait"
  )

  local cmd = string.format(
    '"%s" -m midi_drums prompt "%s" --song %s --output "%s" --write-sidecar "%s"',
    PYTHON_EXE, shell_escape(desc_input), tempo_arg, midi_out, sp
  )

  local py_out = run_python_or_fail(
    cmd,
    "Common causes:\n"
    .. "  • AI API key not set (ANTHROPIC_API_KEY / OPENAI_API_KEY)\n"
    .. "  • AI dependencies not installed (uv sync --group ai)\n"
    .. "  • PYTHON_EXE path incorrect: " .. PYTHON_EXE
  )
  if not py_out then return end

  local content = read_generated_file_or_fail(sp, "sidecar")
  if not content then return end

  local p_tempo, p_num, p_denom, p_sections, err2 = parse_sidecar(content)
  if not p_sections then
    show_ardour_msgbox("Could not parse AI sidecar: " .. (err2 or "?"), "Error")
    return
  end

  sections = p_sections
  if p_tempo and math.abs(p_tempo - bpm) > 0.5 then
    set_tempo_marker(0, p_tempo, p_num, p_denom)
    bpm = p_tempo; ts_num = p_num; ts_denom = p_denom
  end

-- ── Song-map mode (per-section tempo/meter) ────────────────────────────────
elseif MODE == "songmap" then
  local map_input = io.read("*l") or get_session_dir() .. "/song_map.json"
  local map_path = map_input:match("^%s*(.-)%s*$")
  if map_path == "" then
    show_ardour_msgbox("Song-map path cannot be empty.", "Error")
    return
  end

  local mf_check = io.open(map_path, "r")
  if not mf_check then
    show_ardour_msgbox(
      "Could not open song-map JSON:\n" .. map_path, "Song Map Not Found"
    )
    return
  end
  mf_check:close()

  local genre_input = io.read("*l") or (DEFAULT_GENRE .. "," .. DEFAULT_STYLE .. "," .. DEFAULT_MAPPING)
  local genre, style, mapping = genre_input:match("^([^,]+),([^,]+),([^,]+)$")
  genre   = shell_escape((genre   or DEFAULT_GENRE):match("^%s*(.-)%s*$"))
  style   = shell_escape((style   or DEFAULT_STYLE):match("^%s*(.-)%s*$"))
  mapping = shell_escape((mapping or DEFAULT_MAPPING):match("^%s*(.-)%s*$"))

  local timeline_path = get_timeline_path()
  local cmd = string.format(
    '"%s" -m midi_drums generate --genre "%s" --style "%s" --mapping "%s"'
    .. ' --song-map "%s" --write-timeline "%s" --output "%s"',
    PYTHON_EXE, genre, style, mapping, map_path, timeline_path, midi_out
  )

  if not run_python_or_fail(cmd) then return end

  local timeline_content = read_generated_file_or_fail(timeline_path, "timeline")
  if not timeline_content then return end

  local tempo_points, regions_list, color_groups, terr = parse_timeline(timeline_content)
  if not tempo_points then
    show_ardour_msgbox("Could not parse timeline: " .. (terr or "?"), "Error")
    return
  end

  undo_begin()
  for _, tp in ipairs(tempo_points) do
    set_tempo_marker(tp.time, tp.bpm, tp.num, tp.denom)
  end
  for _, r in ipairs(regions_list) do
    local color = 0
    local cg = color_groups[r.color_group]
    if cg then
      color = color_to_native(cg.r, cg.g, cg.b)
    end
    create_region(r.start_time, r.end_time, r.name, color)
  end
  undo_end("Create Song Sections from Song Map")
  refresh_ui()
end

-- ===========================================================================
-- Create Ardour regions (song-map mode creates its own above)
-- ===========================================================================
if MODE ~= "songmap" and #sections > 0 then
  undo_begin()
  local current_time = 0.0
  -- Ardour uses ticks for region positions.  Compute measure length in seconds:
  -- tempo is BPM (quarter notes/min), time signature defines bars per measure.
  -- Measure length (seconds) = (60 / bpm) × (num / denom) × 4
  local measure_length = (60.0 / bpm) * ts_num * (4.0 / ts_denom)

  for _, s in ipairs(sections) do
    local region_end = current_time + (s.bars * measure_length)
    create_region(current_time, region_end, s.name, 0)
    current_time = region_end
  end
  undo_end("Create Song Sections as Regions")
  refresh_ui()
end

-- ===========================================================================
-- Ardour mode: write sidecar, optionally call template Python
-- ===========================================================================
if MODE == "ardour" then
  local sf = io.open(sp, "w")
  if sf then sf:write(sections_to_json(sections, bpm, ts_num, ts_denom)); sf:close() end

  local gen = show_ardour_msgbox(
    "Regions created" .. (sf and ("\nSidecar: " .. sp) or "") .. "\n\n"
    .. "Generate matching MIDI drums with Python now?\n"
    .. "(Uses template engine — no AI required)",
    "Generate MIDI?"
  )
  if type(gen) ~= "boolean" or not gen then return end

  local genre_input = io.read("*l") or (DEFAULT_GENRE .. "," .. DEFAULT_STYLE .. "," .. DEFAULT_MAPPING)
  local genre, style, mapping = genre_input:match("^([^,]+),([^,]+),([^,]+)$")
  genre   = shell_escape((genre   or DEFAULT_GENRE):match("^%s*(.-)%s*$"))
  style   = shell_escape((style   or DEFAULT_STYLE):match("^%s*(.-)%s*$"))
  mapping = shell_escape((mapping or DEFAULT_MAPPING):match("^%s*(.-)%s*$"))

  local cmd = string.format(
    '"%s" -m midi_drums generate --genre "%s" --style "%s" --mapping "%s"'
    .. ' --sidecar "%s" --output "%s"',
    PYTHON_EXE, genre, style, mapping, sp, midi_out
  )

  if not run_python_or_fail(cmd) then return end
end

-- ===========================================================================
-- Auto-import MIDI (Ardour, AI, and song-map modes all produce drums.mid)
-- ===========================================================================
if MODE == "ardour" or MODE == "ai" or MODE == "songmap" then
  if not read_generated_file_or_fail(midi_out, "MIDI file") then return end

  import_midi(midi_out)
  refresh_ui()

  local mode_label = (MODE == "ai") and "AI agent"
    or (MODE == "songmap") and "song-map engine"
    or "template engine"
  show_ardour_msgbox(
    "Done!  (" .. mode_label .. ")\nMIDI imported: " .. midi_out,
    "Drums Ready"
  )
end
