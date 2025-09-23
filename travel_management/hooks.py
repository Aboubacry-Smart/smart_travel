# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """
    Migrate legacy hour_start/hour_end fields from travel.route into
    travel.route.line records, if the legacy columns still exist.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Check if legacy columns exist in database
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'travel_route' AND column_name IN ('hour_start', 'hour_end')
    """)
    cols = {r[0] for r in cr.fetchall()}
    if not {'hour_start', 'hour_end'}.issubset(cols):
        return  # Nothing to migrate

    # Fetch routes with non-null hours
    cr.execute("""
        SELECT id, hour_start, hour_end
        FROM travel_route
        WHERE hour_start IS NOT NULL AND hour_end IS NOT NULL
    """)
    rows = cr.fetchall()

    RouteLine = env['travel.route.line'].sudo()
    for route_id, hour_start, hour_end in rows:
        # Skip invalid data
        try:
            hs = float(hour_start)
            he = float(hour_end)
        except Exception:
            continue
        if hs >= he:
            continue
        # Create a line if none exists yet for this pair
        existing = RouteLine.search([
            ('route_id', '=', route_id),
            ('hour_start', '=', hs),
            ('hour_end', '=', he),
        ], limit=1)
        if not existing:
            RouteLine.create({
                'route_id': route_id,
                'hour_start': hs,
                'hour_end': he,
            })
