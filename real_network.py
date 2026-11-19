"""
Real-World & Multi-Scale Road Network Module
═════════════════════════════════════════════
Defines:
  1. Real Manhattan Urban Network (42 named intersections, real GPS coordinates,
     major avenues, cross streets, arterial corridors like FDR Drive, and 
     critical medical hubs like Bellevue Hospital and NYU Langone).
  2. 6×6 Scaled Urban Grid (36 nodes, 60 edges) for mathematical scalability testing.
  3. Dynamic disruption injection utilities for real-world scenarios.
"""

import copy
import networkx as nx

# ═══════════════════════════════════════════════════════════════════════════════
# 1. REAL MANHATTAN ROAD NETWORK (42 Nodes, Authentically Parameterized)
# ═══════════════════════════════════════════════════════════════════════════════

MANHATTAN_NODES = {
    # NodeID: (Name, Latitude, Longitude, Category)
    "M01": ("Columbus Circle", 40.7681, -73.9819, "transit_hub"),
    "M02": ("Central Park South & 5th Ave", 40.7648, -73.9731, "landmark"),
    "M03": ("Upper East Midtown (Lex & 59th)", 40.7626, -73.9680, "intersection"),
    "M04": ("Queensboro Bridge Ramp (1st & 59th)", 40.7594, -73.9602, "arterial"),
    "M05": ("Theater District North (8th & 50th)", 40.7628, -73.9862, "intersection"),
    "M06": ("Rockefeller Center (5th & 50th)", 40.7587, -73.9787, "landmark"),
    "M07": ("Midtown East Commercial (Lex & 50th)", 40.7567, -73.9734, "intersection"),
    "M08": ("Sutton Place Access (1st & 50th)", 40.7538, -73.9657, "arterial"),
    "M09": ("Port Authority Terminal (8th & 42nd)", 40.7573, -73.9902, "transit_hub"),
    "M10": ("Times Square (Broadway & 42nd)", 40.7562, -73.9866, "landmark"),
    "M11": ("Bryant Park (6th & 42nd)", 40.7536, -73.9832, "landmark"),
    "M12": ("Grand Central Terminal (Park & 42nd)", 40.7527, -73.9772, "transit_hub"),
    "M13": ("Chrysler Building (Lex & 42nd)", 40.7516, -73.9754, "landmark"),
    "M14": ("United Nations Plaza (1st & 42nd)", 40.7489, -73.9680, "arterial"),
    "M15": ("Hudson Yards Transit (11th & 34th)", 40.7554, -74.0022, "transit_hub"),
    "M16": ("Penn Station (8th & 34th)", 40.7512, -73.9934, "transit_hub"),
    "M17": ("Herald Square (Broadway & 34th)", 40.7497, -73.9878, "landmark"),
    "M18": ("Empire State Building (5th & 34th)", 40.7484, -73.9857, "landmark"),
    "M19": ("Murray Hill (Lex & 34th)", 40.7461, -73.9796, "intersection"),
    "M20": ("Bellevue Hospital Center", 40.7392, -73.9748, "hospital_emergency"),
    "M21": ("NYU Langone Medical Center", 40.7421, -73.9739, "hospital_emergency"),
    "M22": ("High Line West (10th & 28th)", 40.7511, -74.0040, "intersection"),
    "M23": ("Chelsea North (8th & 28th)", 40.7473, -73.9959, "intersection"),
    "M24": ("Chelsea Market / High Line (10th & 23rd)", 40.7468, -74.0055, "intersection"),
    "M25": ("Chelsea Transit Hub (8th & 23rd)", 40.7441, -73.9984, "transit_hub"),
    "M26": ("Flatiron Building (5th & 23rd)", 40.7411, -73.9897, "landmark"),
    "M27": ("Gramercy Park (Lex & 23rd)", 40.7388, -73.9840, "landmark"),
    "M28": ("VA Medical Center East (1st & 23rd)", 40.7360, -73.9772, "hospital_emergency"),
    "M29": ("Meatpacking District (10th & 14th)", 40.7408, -74.0080, "intersection"),
    "M30": ("14th St / 8th Ave Station", 40.7382, -74.0016, "transit_hub"),
    "M31": ("Union Square (Broadway & 14th)", 40.7359, -73.9911, "transit_hub"),
    "M32": ("Stuyvesant Town North (1st & 14th)", 40.7307, -73.9809, "intersection"),
    "M33": ("FDR Drive & 14th St Ramp", 40.7280, -73.9734, "arterial"),
    "M34": ("West Village (7th & Bleecker)", 40.7328, -74.0045, "intersection"),
    "M35": ("Washington Square (5th Ave Arch)", 40.7308, -73.9973, "landmark"),
    "M36": ("East Village Center (2nd & 8th)", 40.7284, -73.9877, "intersection"),
    "M37": ("SoHo North (Broadway & Houston)", 40.7251, -73.9961, "intersection"),
    "M38": ("Lower East Side (Bowery & Houston)", 40.7239, -73.9918, "intersection"),
    "M39": ("FDR Drive & Houston Ramp", 40.7208, -73.9752, "arterial"),
    "M40": ("Holland Tunnel Portal (Canal & Varick)", 40.7214, -74.0084, "arterial"),
    "M41": ("Chinatown Center (Canal & Centre)", 40.7180, -73.9998, "transit_hub"),
    "M42": ("Financial District (Broadway & Wall)", 40.7071, -74.0110, "transit_hub")
}

# Real Named Corridors with realistic travel times (minutes) and capacities
MANHATTAN_EDGES = [
    # ── East-West 59th St Crossway ───────────────────────────────────────────
    ("M01", "M02", "Central Park South", 4.0, 50),
    ("M02", "M03", "E 59th Street", 3.5, 45),
    ("M03", "M04", "Queensboro Approach (E 59th)", 4.0, 60),

    # ── East-West 50th St Corridor ───────────────────────────────────────────
    ("M05", "M06", "W 50th Street", 4.5, 40),
    ("M06", "M07", "E 50th Street", 3.5, 40),
    ("M07", "M08", "E 50th St East Link", 4.0, 45),

    # ── East-West 42nd St Transverse (Major Transit Corridor) ────────────────
    ("M09", "M10", "W 42nd St (Theater Row)", 3.0, 40),
    ("M10", "M11", "W 42nd St (Times Sq - Bryant Pk)", 2.5, 35),
    ("M11", "M12", "E 42nd St (Library - Grand Central)", 3.5, 45),
    ("M12", "M13", "E 42nd St (Grand Central - Chrysler)", 2.0, 45),
    ("M13", "M14", "E 42nd St to UN Plaza", 4.0, 55),

    # ── East-West 34th St Transverse (Penn - Empire - Hospitals) ────────────
    ("M15", "M16", "W 34th St (Hudson Yards - Penn)", 4.0, 55),
    ("M16", "M17", "W 34th St (Penn - Herald Sq)", 3.0, 40),
    ("M17", "M18", "W 34th St (Herald Sq - Empire State)", 2.5, 40),
    ("M18", "M19", "E 34th St (Empire - Murray Hill)", 3.5, 45),
    ("M19", "M21", "E 34th St to NYU Langone", 3.0, 50),
    ("M21", "M20", "Hospital Transit Link (NYU to Bellevue)", 2.0, 60),

    # ── East-West 23rd St Transverse (Chelsea - Flatiron - VA Hospital) ─────
    ("M24", "M25", "W 23rd St (Chelsea)", 3.5, 45),
    ("M25", "M26", "W 23rd St (Chelsea - Flatiron)", 4.0, 40),
    ("M26", "M27", "E 23rd St (Flatiron - Gramercy)", 3.5, 40),
    ("M27", "M28", "E 23rd St to VA Medical Center", 3.5, 50),

    # ── East-West 14th St Transverse (Meatpacking - Union Sq - FDR) ─────────
    ("M29", "M30", "W 14th St (Meatpacking - 8th Ave)", 3.5, 45),
    ("M30", "M31", "W 14th St (8th Ave - Union Square)", 4.0, 40),
    ("M31", "M32", "E 14th St (Union Sq - 1st Ave)", 4.5, 40),
    ("M32", "M33", "E 14th St to FDR Ramp", 3.5, 55),

    # ── Houston St & Lower Arterials ─────────────────────────────────────────
    ("M34", "M35", "W 4th St (West Village - Wash Sq)", 3.5, 35),
    ("M35", "M37", "Houston St West (SoHo Link)", 4.0, 45),
    ("M37", "M38", "E Houston St (SoHo - Lower East Side)", 3.5, 50),
    ("M38", "M39", "E Houston St to FDR Drive Ramp", 3.5, 55),
    ("M40", "M41", "Canal Street (Holland Tunnel to Chinatown)", 5.0, 60),
    ("M41", "M42", "Broadway South to Wall Street", 6.0, 45),

    # ── Major North-South Avenues ────────────────────────────────────────────
    # 8th Avenue Corridor (Downtown flow)
    ("M01", "M05", "8th Avenue North", 4.0, 50),
    ("M05", "M09", "8th Avenue Midtown", 3.5, 45),
    ("M09", "M16", "8th Avenue (Port Authority - Penn)", 4.0, 45),
    ("M16", "M23", "8th Avenue Garment Link", 3.0, 40),
    ("M23", "M25", "8th Avenue Chelsea", 2.5, 40),
    ("M25", "M30", "8th Avenue South to 14th St", 4.0, 45),
    ("M30", "M34", "Greenwich / 7th Ave South", 4.5, 40),

    # Broadway / 7th Ave (Midtown Spine)
    ("M05", "M10", "Broadway / 7th Ave Theater Link", 4.0, 45),
    ("M10", "M17", "Broadway (Times Sq to Herald Sq)", 4.5, 40),
    ("M17", "M26", "Broadway (Herald Sq to Flatiron)", 5.0, 40),
    ("M26", "M31", "Broadway (Flatiron to Union Sq)", 4.0, 45),
    ("M31", "M35", "Broadway / University Pl to Wash Sq", 4.0, 40),
    ("M35", "M37", "Broadway SoHo Arterial", 3.5, 40),
    ("M37", "M41", "Broadway South to Canal St", 4.5, 45),

    # 5th Avenue Corridor (Prestigious Central Spine)
    ("M02", "M06", "5th Avenue North (Plaza to Rock Ctr)", 4.0, 50),
    ("M06", "M11", "5th Avenue Midtown (Rock Ctr to 42nd)", 4.0, 45),
    ("M11", "M18", "5th Avenue (42nd to Empire State)", 3.5, 45),
    ("M18", "M26", "5th Avenue (Empire State to Flatiron)", 5.0, 45),
    ("M26", "M35", "5th Avenue South to Washington Sq", 5.5, 40),

    # Park / Lexington Avenues Corridor
    ("M03", "M07", "Lexington Ave North", 3.5, 50),
    ("M07", "M13", "Lexington Ave (50th to Chrysler)", 3.5, 45),
    ("M12", "M19", "Park Ave Tunnel / Murray Hill Link", 4.0, 55),
    ("M13", "M19", "Lexington Ave to 34th St", 4.0, 45),
    ("M19", "M27", "Lexington Ave to Gramercy", 4.5, 40),
    ("M27", "M31", "Irving Pl / Park Ave South to Union Sq", 4.0, 45),

    # 1st Avenue Corridor (East Side Medical Spine)
    ("M04", "M08", "1st Avenue North (59th to 50th)", 3.5, 50),
    ("M08", "M14", "1st Avenue Midtown (50th to UN)", 3.5, 50),
    ("M14", "M21", "1st Avenue to NYU Langone Center", 4.5, 55),
    ("M20", "M28", "1st Avenue (Bellevue to VA Hospital)", 2.5, 60),
    ("M28", "M32", "1st Avenue to 14th St", 3.5, 50),
    ("M32", "M36", "1st Avenue / East Village", 3.5, 45),
    ("M36", "M38", "2nd Avenue to Houston St", 3.5, 45),

    # FDR Drive Arterial Highway (High Speed East River Flow)
    ("M14", "M20", "FDR Drive Midtown (UN to Bellevue Ramp)", 3.0, 80),
    ("M20", "M33", "FDR Drive South (Bellevue to 14th St)", 3.0, 80),
    ("M33", "M39", "FDR Drive Lower (14th St to Houston)", 2.5, 80),
    ("M39", "M42", "FDR Drive to Battery / Financial Dist", 4.5, 80),

    # 10th / 11th Ave West Side Links
    ("M15", "M22", "11th Ave High Line Arterial", 3.0, 60),
    ("M22", "M24", "10th Ave Chelsea Link", 3.0, 50),
    ("M24", "M29", "10th Ave to Meatpacking", 3.5, 50),
    ("M29", "M40", "West St / Route 9A to Holland Tunnel", 5.0, 70),
]

# 2D Schematic Layout Coordinates for Crisp, Clean Transit-Map Visualization
MANHATTAN_POSITIONS = {
    # ── 59th St Corridor (Northern Boundary, y = 8.0) ──
    "M01": (2.2, 8.0),   # Columbus Circle (8th Ave / Broadway & 59th)
    "M02": (4.0, 8.0),   # Central Park South & 5th Ave
    "M03": (5.2, 8.0),   # Upper East Midtown (Lexington & 59th)
    "M04": (6.4, 8.0),   # Queensboro Bridge Ramp (1st Ave & 59th)

    # ── 50th St Corridor (Midtown North, y = 7.0) ──
    "M05": (2.2, 7.0),   # Theater District North (8th Ave & 50th)
    "M06": (4.0, 7.0),   # Rockefeller Center (5th Ave & 50th)
    "M07": (5.2, 7.0),   # Midtown East Commercial (Lexington & 50th)
    "M08": (6.4, 7.0),   # Sutton Place Access (1st Ave & 50th)

    # ── 42nd St Transverse (Midtown Central Spine, y = 6.0) ──
    "M09": (2.2, 6.0),   # Port Authority Terminal (8th Ave & 42nd)
    "M10": (3.1, 6.0),   # Times Square (Broadway & 42nd)
    "M11": (3.6, 6.0),   # Bryant Park (6th Ave & 42nd)
    "M12": (4.6, 6.0),   # Grand Central Terminal (Park Ave & 42nd)
    "M13": (5.2, 6.0),   # Chrysler Building (Lexington & 42nd)
    "M14": (6.4, 6.0),   # United Nations Plaza (1st Ave & 42nd)

    # ── 34th St Transverse (Penn Station - Empire State - Medical Hubs, y = 5.0) ──
    "M15": (0.6, 5.0),   # Hudson Yards Transit (11th Ave & 34th)
    "M16": (2.2, 5.0),   # Penn Station (8th Ave & 34th)
    "M17": (3.1, 5.0),   # Herald Square (Broadway & 34th)
    "M18": (4.0, 5.0),   # Empire State Building (5th Ave & 34th)
    "M19": (5.2, 5.0),   # Murray Hill (Lexington & 34th)
    "M21": (6.4, 5.0),   # NYU Langone Medical Center (1st Ave & 34th)
    "M20": (7.4, 4.3),   # Bellevue Hospital Center (FDR / 1st & 28th)

    # ── 28th & 23rd St Transverse (Chelsea - Flatiron - VA Hospital, y ~ 3.5 - 4.3) ──
    "M22": (1.3, 4.3),   # High Line West (10th Ave & 28th)
    "M23": (2.2, 4.3),   # Chelsea North (8th Ave & 28th)
    "M24": (1.3, 3.5),   # Chelsea Market / High Line (10th Ave & 23rd)
    "M25": (2.2, 3.5),   # Chelsea Transit Hub (8th Ave & 23rd)
    "M26": (4.0, 3.5),   # Flatiron Building (5th Ave & 23rd)
    "M27": (5.2, 3.5),   # Gramercy Park (Lexington & 23rd)
    "M28": (6.4, 3.5),   # VA Medical Center East (1st Ave & 23rd)

    # ── 14th St Transverse (Meatpacking - Union Sq - FDR, y = 2.4) ──
    "M29": (1.3, 2.4),   # Meatpacking District (10th Ave & 14th)
    "M30": (2.2, 2.4),   # 14th St / 8th Ave Station
    "M31": (3.5, 2.4),   # Union Square (Broadway & 14th)
    "M32": (6.4, 2.4),   # Stuyvesant Town North (1st Ave & 14th)
    "M33": (7.4, 2.4),   # FDR Drive & 14th St Ramp

    # ── Greenwich Village & Houston St (y ~ 0.8 - 1.5) ──
    "M34": (2.2, 1.5),   # West Village (7th & Bleecker)
    "M35": (3.6, 1.5),   # Washington Square (5th Ave Arch)
    "M36": (5.6, 1.5),   # East Village Center (2nd Ave & 8th)
    "M37": (3.1, 0.8),   # SoHo North (Broadway & Houston)
    "M38": (5.0, 0.8),   # Lower East Side (Bowery & Houston)
    "M39": (7.4, 0.8),   # FDR Drive & Houston Ramp

    # ── Canal St & Lower Manhattan (y ~ -1.0 - 0.0) ──
    "M40": (1.5, 0.0),   # Holland Tunnel Portal (Canal & Varick)
    "M41": (3.1, 0.0),   # Chinatown Center (Canal & Centre)
    "M42": (3.5, -1.0)   # Financial District (Broadway & Wall)
}


def create_real_manhattan_network():
    """Constructs the NetworkX Graph for the Real Manhattan Network."""
    G = nx.Graph()
    for nid, (name, lat, lon, cat) in MANHATTAN_NODES.items():
        pos = MANHATTAN_POSITIONS.get(nid, (0.0, 0.0))
        G.add_node(nid, name=name, lat=lat, lon=lon, category=cat, pos=pos)

    for u, v, street, tt, cap in MANHATTAN_EDGES:
        G.add_edge(u, v, street_name=street, travel_time=tt, free_flow_time=tt, capacity=cap)

    return G


# ═══════════════════════════════════════════════════════════════════════════════
# 2. EXPANDED 6×6 URBAN DISTRICT (36 Nodes, 60 Edges)
# ═══════════════════════════════════════════════════════════════════════════════

def create_6x6_scaled_network():
    """
    Constructs a 6×6 Manhattan-style grid (36 nodes: S00 to S35, 60 edges)
    for controlled mathematical scalability stress-testing.
    """
    G = nx.Graph()
    # 36 nodes
    for r in range(6):
        for c in range(6):
            idx = r * 6 + c
            nid = f"S{idx:02d}"
            name = f"Sector {r+1}-{chr(65+c)}"
            G.add_node(nid, pos=(c, 5 - r), name=name, row=r, col=c)

    # 60 bidirectional edges
    for r in range(6):
        for c in range(6):
            idx = r * 6 + c
            u = f"S{idx:02d}"
            # Horizontal edge
            if c < 5:
                v = f"S{idx+1:02d}"
                tt = 4.0 + (r + c) % 3
                G.add_edge(u, v, street_name=f"Transverse R{r+1}-H", travel_time=tt, free_flow_time=tt, capacity=45)
            # Vertical edge
            if r < 5:
                v = f"S{idx+6:02d}"
                tt = 5.0 + (r * c) % 3
                G.add_edge(u, v, street_name=f"Avenue C{c+1}-V", travel_time=tt, free_flow_time=tt, capacity=45)

    return G


# ═══════════════════════════════════════════════════════════════════════════════
# 3. DISRUPTION INJECTION HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def apply_real_disruptions(G_orig, disruptions):
    """
    Applies real-world road closures and congestion bottlenecks to graph G.
    Returns: (G_disrupted, set_of_closed_edges)
    """
    G = copy.deepcopy(G_orig)
    closed = set()
    for d in disruptions:
        if d.get("type") == "road_closure" and "edge" in d:
            u, v = d["edge"]
            if G.has_edge(u, v):
                G.remove_edge(u, v)
                closed.add((u, v))
                closed.add((v, u))
        elif d.get("type") == "congestion" and "edge" in d:
            u, v = d["edge"]
            if G.has_edge(u, v):
                G[u][v]["travel_time"] *= d.get("factor", 3.0)
    return G, closed
