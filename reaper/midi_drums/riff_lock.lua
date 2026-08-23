-- reaper/midi_drums/riff_lock.lua
-- Riff-lock helpers: compute bar alignment, render audio from selection,
-- build Python CLI command for riff-locked beat generation.

local sections = dofile(debug.getinfo(1).path:match("^(.*)[\\/][^\\/]+$") .. "sections.lua")
local M = {}

function M.get_project_dir()
  return sections.get_project_dir()
end

-- ===== Bar alignment math =====

-- Computes how far the selected item's start sits from its enclosing bar line,
-- in quarter notes. Returns (offset_beats, bar_start_qn, bar_end_qn, ts_num,
-- ts_denom, bpm). A riff that doesn't start on a bar line would otherwise get
-- its accents locked to a phase-shifted reading — this corrects that.
function M.compute_bar_alignment(item)
  local item_start = reaper.GetMediaItemInfo_Value(item, "D_POSITION")
  local item_qn = reaper.TimeMap2_timeToQN(0, item_start)

  local ts_num, ts_denom, bpm = reaper.TimeMap_GetTimeSigAtTime(0, item_start)
  if not ts_num or ts_num == 0 then ts_num, ts_denom = 4, 4 end
  if not bpm or bpm == 0 then bpm = reaper.Master_GetTempo() end

  local qn_per_bar = ts_num * (4.0 / ts_denom)
  local bar_index = math.floor(item_qn / qn_per_bar + 1e-9)
  local bar_start_qn = bar_index * qn_per_bar
  local bar_end_qn = bar_start_qn + qn_per_bar
  local offset_beats = item_qn - bar_start_qn

  return offset_beats, bar_start_qn, bar_end_qn, ts_num, ts_denom, bpm
end

-- ===== Audio rendering =====

function M.resolve_audio_source(item, take, bar_start_qn, bar_end_qn)
  local path = reaper.GetMediaItemTake_Source(take)
  if not path then return nil, nil, nil, "No source for selected item." end

  -- Save current time selection
  local ts_start_old, ts_end_old, ts_active =
    reaper.GetSet_LoopTimeSelection(0, 0, 0, 0, 0)

  -- Set time selection to bar range (in seconds)
  local bar_start_time = reaper.TimeMap2_QNToTime(0, bar_start_qn)
  local bar_end_time = reaper.TimeMap2_QNToTime(0, bar_end_qn)
  reaper.GetSet_LoopTimeSelection(0, 1, bar_start_time, bar_end_time, 0)

  -- Render to temp WAV (use most recent render settings: "RENDER_FILE"=42230)
  local tmp_dir = os.getenv("TEMP") or "."
  local wav_path = tmp_dir .. "/midi_drums_riff_" ..
    string.format("%d", math.floor(reaper.time_precise() * 1000)) .. ".wav"

  -- Use REAPER's render function with bounds flag (time selection)
  local success = reaper.Project_ForceProjectExporter(
    -1, wav_path, "RENDER_FILE", true, -- save/restore format settings
    false -- don't open in editor
  )

  if not success then
    -- Fallback: try manual render path
    reaper.GetSet_LoopTimeSelection(0, 0, ts_start_old, ts_end_old, 0)
    return nil, nil, nil, "Failed to render audio. Check render settings."
  end

  reaper.GetSet_LoopTimeSelection(0, 0, ts_start_old, ts_end_old, 0)
  return wav_path, 0, bar_end_time - bar_start_time, nil
end

-- ===== CLI command builder =====

function M.build_cmd(python_exe, params)
  -- Delegate to sections.lua build_riff_cmd (our CLI contract)
  return sections.build_riff_cmd(python_exe, params)
end

-- ===== Job complete handler =====

function M.on_job_complete(params)
  local sections = dofile(debug.getinfo(1).path:match("^(.*)[\\/][^\\/]+$") .. "sections.lua")
  return sections.on_riff_complete(params)
end

return M
