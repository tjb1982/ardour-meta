ardour {
	["type"]    = "EditorAction",
	name        = "Ardour-meta: update marker info",
	license     = "MIT",
	author      = "Tom Brennan",
	description = [[Update the range info of the selected marker.]]
}

--function action_params ()
--	return
--	{
--		["unique"]   = { title = "Only add HPF/LPF if not already present (yes/no)", default = "yes"},
--		["position"] = { title = "Insert Position from top (0,..)",                   default = "0"},
--	}
--end

-- tjb 0.1.0

function factory (params)
    local SEP = " "

    local ardour_meta_dir = Session:path() .. "/.ardour-meta"
    os.execute("mkdir -p " .. ardour_meta_dir)

    function ensure_session_id ()
        local f = io.open(ardour_meta_dir .. "/session-id", "a+")
        local ts = f:read()
        if ts then
            -- `read` a single line at a time (we only want one)
            return ts
        else
            local ts = os.time()
            f:write(ts)
            f:close()
            return ts
        end
    end

    function base_cmd ()
        -- XXX: `user_config_directory(-1)` gives us the path to the user's
        -- database; i.e., that holds data for all different sessions, not
        -- just this one.
        return "ardour-meta" .. SEP
        .. "'" .. ARDOUR.user_config_directory(-1) .. "'" .. SEP
        .. "'" .. Session:name() .. "'" .. SEP
        .. "'" .. ardour_meta_dir .. "'" .. SEP
    end
    
    function launch_location_editors ()
        local locations = {}
    
        for m in Editor:get_selection().markers:iter() do
            for l in Session:locations():list():iter() do
                key = l:name() .. "," .. l:start() .. "," .. l:_end()
                if m:position() == l:start() then
                    locations[key] = l
                elseif m:position() == l:_end() then
                    locations[key] = l
                end
            end
        end
    
        for _, location in pairs(locations) do
            io.popen(
                base_cmd()
                .. "range" .. SEP
                .. "'" .. location:name() .. "'" .. SEP
                .. location:start() .. SEP
                .. location:_end()
            )
        end
    end
    
    function launch_region_editors ()
        regionlist = Editor:get_selection().regions:regionlist()
    
        for r in regionlist:iter() do
            io.popen(
                base_cmd()
                .. "region" .. SEP
                .. "'" .. r:name() .. "'" .. SEP
                .. r:start() .. SEP
                .. r:length()
            )
        end
    end
    
    return function ()
        ensure_session_id()
        launch_location_editors()
        launch_region_editors()
    end
end
