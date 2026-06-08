-- mpv Lua script: show photo date + location from a lookup file
-- Lookup file: one line per entry, tab-separated: path\tinfo_text

local lookup = {}
local lookup_file = os.getenv("PHOTOSHUFFLER_INFO") or "/tmp/photoshuffler-info.txt"

local function load_lookup()
    local f = io.open(lookup_file, "r")
    if not f then return end
    for line in f:lines() do
        local path, info = line:match("^(.-)\t(.+)$")
        if path then lookup[path] = info end
    end
    f:close()
end

load_lookup()

local function on_file_loaded()
    local path = mp.get_property("path")
    local info = lookup[path] or ""
    mp.set_property("osd-msg1", info)
end

mp.register_event("file-loaded", on_file_loaded)
