#!/usr/bin/env python3
"""
Step 15: Run SUMO with live GUI (sumo-gui)
Starts the native Eclipse SUMO graphical simulator window,
visualizes the 4x4 road network, steps through time, and injects disruptions live.
"""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import traci

def main():
    net_file = "networks/grid_4x4.net.xml"
    if not os.path.exists(net_file):
        print(f"Error: Network file not found at {net_file}")
        sys.exit(1)

    # Minimal SUMO configuration XML
    cfg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="{os.path.abspath(net_file)}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="400"/>
    </time>
    <gui_only>
        <start value="true"/>
    </gui_only>
</configuration>"""
    
    cfg_path = "networks/test_visual.sumocfg"
    with open(cfg_path, 'w') as f:
        f.write(cfg_content)
    
    print(f"Starting Eclipse SUMO GUI on network: {net_file}")
    print("A graphical window will open. Click 'Play' or watch the simulation step automatically.")
    
    # Launch sumo-gui via TraCI
    try:
        traci.start(["sumo-gui", "-c", cfg_path, "--delay", "50", "--window-size", "1000,750"])
    except Exception as e:
        print(f"Could not launch sumo-gui via TraCI: {e}")
        print("Alternative command to open GUI directly:")
        print(f"  sumo-gui -n {net_file}")
        return

    print("\nSUMO GUI is active! Running steps...")
    
    try:
        for step in range(300):
            traci.simulationStep()
            
            # Demonstrate dynamic disruption injection at step 50
            if step == 50:
                print(">>> Step 50: Injecting live road closure on link B2C2...")
                try:
                    for lane_idx in range(2):
                        lane_id = f"B2C2_{lane_idx}"
                        traci.lane.setDisallowed(lane_id, ["passenger", "bus", "taxi"])
                    traci.edge.adaptTraveltime("B2C2", time=100000)
                    print(">>> Road closure applied live in SUMO!")
                except Exception as ex:
                    print(f"TraCI injection note: {ex}")
            
            time.sleep(0.02)
    except traci.exceptions.FatalTraCIError:
        print("SUMO GUI window closed by user.")
    finally:
        try:
            traci.close()
        except Exception:
            pass

    print("Visual test complete.")

if __name__ == "__main__":
    main()
