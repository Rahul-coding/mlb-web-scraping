from html import escape


def build_html(leaders_data, previous_date=None, categories=None):
    html = """
    <html>
      <head>
        <style>
          body {
            font-family: Arial, sans-serif;
            color: #0f172a;
            line-height: 1.5;
            background: #f8fafc;
          }
          h2 {
            color: #1e3a8a;
          }
          h3 {
            color: #2563eb;
          }
          h4 {
            color: #334155;
            margin-bottom: 4px;
          }
          ol {
            padding-left: 20px;
          }
          li {
            margin: 6px 0;
          }
          .name {
            font-weight: bold;
          }
          .context {
            margin: 0 0 18px;
            color: #475569;
          }
          .category-note {
            margin: 0 0 8px;
            color: #334155;
            font-size: 0.95rem;
          }
          .new-badge {
            display: inline-block;
            margin-left: 8px;
            padding: 2px 8px;
            border-radius: 999px;
            color: #166534;
            font-size: 0.75rem;
            font-weight: bold;
            letter-spacing: 0.02em;
            vertical-align: middle;
            background: #bbf7d0;
          }
          .up-badge {
            display: inline-block;
            margin-left: 8px;
            padding: 2px 8px;
            border-radius: 999px;
            background: #dcfce7;
            color: #065f46;
            font-size: 0.75rem;
            font-weight: bold;
            vertical-align: middle;
          }
          .down-badge {
            display: inline-block;
            margin-left: 8px;
            padding: 2px 8px;
            border-radius: 999px;
            background: #fee2e2;
            color: #7f1d1d;
            font-size: 0.75rem;
            font-weight: bold;
            vertical-align: middle;
          }
          .removed-player {
            color: #7f1d1d;
            text-decoration: line-through;
          }
          .removed-badge {
            display: inline-block;
            margin-left: 8px;
            padding: 2px 8px;
            border-radius: 999px;
            color: #991b1b;
            font-size: 0.75rem;
            font-weight: bold;
            letter-spacing: 0.02em;
            vertical-align: middle;
            background: #fecaca;
          }
        </style>
      </head>
      <body>
        <h2>MLB League Leaders</h2>
    """

    # Build a mapping from label -> group (hitting/pitching) if categories provided
    label_group = {}
    if categories:
        try:
            for _, (lab, grp) in categories.items():
                label_group[lab] = grp
        except Exception:
            label_group = {}

    # Group labels by their group
    groups = {}
    for label in leaders_data.keys():
        if label.endswith("_removed"):
            continue
        grp = label_group.get(label, "hitting")
        groups.setdefault(grp, []).append(label)

    # render each group separately (e.g., Hitters, Pitchers)
    for grp, labels in groups.items():
        title = "Hitters" if grp == "hitting" else "Pitchers" if grp == "pitching" else grp.title()
        html += f"<h3>{escape(title)}</h3>"
        for label in labels:
            players = leaders_data.get(label, [])
            removed_players = leaders_data.get(f"{label}_removed", [])

            html += f"<h4>{escape(label)} Leaders</h4>"
            html += "<ol>"

            for player in players:
                player_class = "new-player" if player.get("is_new") else ""
                new_badge = '<span class="new-badge">NEW</span>' if player.get("is_new") else ""
                up_badge = ""
                from_rank = player.get("from_rank")
                if player.get("moved_up"):
                  up_badge = f'<span class="up-badge">▲{from_rank}</span>'
                elif player.get("moved_down"):
                  up_badge = f'<span class="down-badge>▼{from_rank}</span>'

                html += f"""
                <li class="{player_class}">
                  <span class="name">{escape(player['name'])}</span>{new_badge}{up_badge}
                  ({escape(player['team'])}) — {escape(str(player['value']))}
                </li>
                """

            # render removed players (if any) in the same list with removed styling
            for player in removed_players:
                html += f"""
                <li class="removed-player">
                  <span class="name">{escape(player['name'])}</span><span class="removed-badge">REMOVED</span>
                  ({escape(player['team'])}) — {escape(str(player['value']))}
                </li>
                """

            html += "</ol>"

    html += "</body></html>"
    html += "Baseball stats comparison: https://mlbstatscompare.streamlit.app/"

    return html
