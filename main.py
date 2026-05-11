# snippet of the new incidental logic being added to your deployment
def calculate_incidentals(primary_item):
    incidentals = []
    if "Luxury Vinyl Plank" in primary_item['description']:
        # Add Transition Strips
        incidentals.append({
            "code": "09 65 13",
            "trade": "Flooring",
            "description": "Transition Strips (Matching LVP)",
            "order_qty": "4 Pcs",
            "pricing": {"low": "$120", "avg": "$160", "high": "$240"},
            "labor": {"low": "$80", "avg": "$100", "high": "$150"}
        })
        # Add Quarter Round
        incidentals.append({
            "code": "06 20 00",
            "trade": "Carpentry",
            "description": "Quarter Round Molding - White",
            "order_qty": "160 LF",
            "pricing": {"low": "$160", "avg": "$200", "high": "$320"},
            "labor": {"low": "$320", "avg": "$480", "high": "$640"}
        })
    return incidentals
