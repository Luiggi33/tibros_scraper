from tibros_scraper import main

from tibros_scraper.main import build_discord_payload, grades_changed, hash_exam_results, load_grade_hash, parse_exam_results, save_grade_hash

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


def test_build_discord_payload_can_ping_a_user():
    results = [
        {
            'label': 'Konzeption und Administration von IT-Systemen',
            'points': '92',
            'mark': '1.0',
        },
    ]

    payload = build_discord_payload(
        results,
        content='<@367690502432227329> Grades changed on IHK Berlin.',
        allowed_mentions={'users': ['367690502432227329']},
        timestamp='2026-06-01T15:45:00.000Z',
    )

    assert payload['content'] == '<@367690502432227329> Grades changed on IHK Berlin.'
    assert payload['allowed_mentions'] == {'users': ['367690502432227329']}


def test_grade_hash_round_trip_and_change_detection(tmp_path):
    snapshot_path = tmp_path / 'grades.json'
    previous_results = [
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

    save_grade_hash(snapshot_path, previous_results)

    loaded_results = load_grade_hash(snapshot_path)
    expected_hash = hash_exam_results(previous_results)

    assert loaded_results == expected_hash
    assert grades_changed(loaded_results, previous_results) is False

    updated_results = [
        {
            'label': 'Einrichten eines IT-gestützten Arbeitsplatzes',
            'points': '88',
            'mark': '2.0',
        },
        {
            'label': 'Konzeption und Administration von IT-Systemen',
            'points': '92',
            'mark': '1.0',
        },
    ]

    assert grades_changed(loaded_results, updated_results) is True


def test_create_webdriver_uses_remote_selenium(monkeypatch):
    captured = {}

    class DummyDriver:
        pass

    def fake_remote(*, command_executor, options):
        captured['command_executor'] = command_executor
        captured['options'] = options
        return DummyDriver()

    def fail_local(*args, **kwargs):
        raise AssertionError('local Chrome driver should not be used when SELENIUM_REMOTE_URL is set')

    monkeypatch.setenv('SELENIUM_REMOTE_URL', 'http://selenium:4444')
    monkeypatch.delenv('CHROMEDRIVER_PATH', raising=False)
    monkeypatch.setattr(main.webdriver, 'Remote', fake_remote)
    monkeypatch.setattr(main.webdriver, 'Chrome', fail_local)

    driver = main.create_webdriver()

    assert isinstance(driver, DummyDriver)
    assert captured['command_executor'] == 'http://selenium:4444'
    assert '--headless' in captured['options'].arguments


def test_create_webdriver_uses_local_chromedriver_when_remote_is_unset(monkeypatch):
    captured = {}

    class DummyDriver:
        pass

    def fake_chrome(*, service, options):
        captured['service'] = service
        captured['options'] = options
        return DummyDriver()

    monkeypatch.delenv('SELENIUM_REMOTE_URL', raising=False)
    monkeypatch.setenv('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
    monkeypatch.setattr(main.webdriver, 'Chrome', fake_chrome)

    driver = main.create_webdriver()

    assert isinstance(driver, DummyDriver)
    assert captured['service'].path == '/usr/bin/chromedriver'
    assert '--disable-dev-shm-usage' in captured['options'].arguments
