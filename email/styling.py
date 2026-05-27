def build_html(leaders_data):
    html = """
    <html>
      <head>
        <style>
          body {
            font-family: Arial;
          }
          h2 {
            color: #1e3a8a;
          }
          h3 {
            color: #2563eb;
          }
          ol {
            padding-left: 20px;
          }
          li {
            margin: 5px 0;
          }
          .name {
            font-weight: bold;
          }
        </style>
      </head>
      <body>
        <h2>MLB League Leaders</h2>
    """

    for label, players in leaders_data.items():

        html += f"<h3>{label} Leaders</h3><ol>"

        for player in players:
            html += f"""
            <li>
              <span class="name">{player['name']}</span>
              ({player['team']}) — {player['value']}
            </li>
            """

        html += "</ol>"

    html += "</body></html>"

    return html