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

function factory (params)
    local SEP = " "

    function session_id()
        local f = io.open(Session:path() .. ".ardour-meta-id", "a+")
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

    function base_cmd()
        return "ardour-meta" .. SEP
        .. "'" .. ARDOUR.user_config_directory(-1) .. "'" .. SEP
        .. "'" .. Session:name() .. "'" .. SEP
        .. "'" .. session_id() .. "'" .. SEP
    end
    
    function launch_location_editors()
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
    
    function launch_region_editors()
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
	    launch_location_editors()
	    launch_region_editors()
    end
end
