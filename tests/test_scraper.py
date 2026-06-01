from tibros_scraper.main import build_discord_payload, parse_exam_results

def test_parse_exam_results_with_valid_data():
    """Test parsing of valid exam results HTML"""
    html_content = """
    <div class="noc_table">
        <div class="row reihe">
            <div class="col-xs-8"><b>Exam Name</b></div>
            <div class="col-xs-2"><b>Points</b></div>
            <div class="col-xs-2"><b>Mark</b></div>
        </div>
        <div class="row reihe">
            <div class="col-xs-8">Einrichten eines IT-gestützten Arbeitsplatzes</div>
            <div class="col-xs-2">85</div>
            <div class="col-xs-2">2.0</div>
        </div>
        <div class="row reihe">
            <div class="col-xs-8">Konzeption und Administration von IT-Systemen</div>
            <div class="col-xs-2">92</div>
            <div class="col-xs-2">1.0</div>
        </div>
    </div>
    """

    results = parse_exam_results(html_content)

    assert len(results) == 2
    assert results[0]['label'] == 'Einrichten eines IT-gestützten Arbeitsplatzes'
    assert results[0]['points'] == '85'
    assert results[0]['mark'] == '2.0'
    assert results[1]['label'] == 'Konzeption und Administration von IT-Systemen'
    assert results[1]['points'] == '92'
    assert results[1]['mark'] == '1.0'

def test_parse_exam_results_with_empty_table():
    """Test parsing when there are no results"""
    html_content = """
    <div class="noc_table">
        <div class="row reihe">
            <div class="col-xs-8"><b>Exam Name</b></div>
            <div class="col-xs-2"><b>Points</b></div>
            <div class="col-xs-2"><b>Mark</b></div>
        </div>
    </div>
    """

    results = parse_exam_results(html_content)

    assert results == []

def test_parse_exam_results_with_no_table():
    """Test parser when something seems wrong."""
    html_content = """
    <div class="container">
        <div class="row">
            <div class="col-xs-12">This is not real</div>
        </div>
    </div>
    """

    results = parse_exam_results(html_content)

    assert results == []


def test_build_discord_payload_uses_labels_and_scores():
    results = [
        {
            'label': 'Einrichten eines IT-gestützten Arbeitsplatzes',
            'points': '85',
            'mark': '2.0',
        },
        {
            'label': 'Konzeption und Administration von IT-Systemen',
            'points': '92',
            'mark': '1.0',
        },
    ]

    payload = build_discord_payload(results, timestamp='2026-06-01T15:45:00.000Z')

    embed = payload['embeds'][0]

    assert embed['title'] == 'IHK Berlin | Prüfungsnoten'
    assert embed['url'] == 'https://apps.ihk-berlin.de/tibrosBB/BB_auszubildende.jsp'
    assert embed['color'] == 5793266
    assert embed['timestamp'] == '2026-06-01T15:45:00.000Z'
    assert embed['fields'] == [
        {
            'name': 'Einrichten eines IT-gestützten Arbeitsplatzes',
            'value': 'Points: 85\nMark: 2.0',
            'inline': True,
        },
        {
            'name': 'Konzeption und Administration von IT-Systemen',
            'value': 'Points: 92\nMark: 1.0',
            'inline': True,
        },
    ]
