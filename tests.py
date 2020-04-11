
def test_duration():
    durations = ['PT1M22S', 'PT10M29S', 'PT3M8S', 'PT2M56S', 'PT2M56S', 'PT2M59S', 'PT2M45S', 'PT3M21S', 'PT2M8S', 'PT2M28S', 'PT2M6S', 'PT1M38S', 'PT1M49S',
                  'PT2M40S', 'PT3M26S',  'PT2M41S', 'PT10M52S', 'PT2M43S', 'PT13M24S', 'PT3M29S', 'PT2M24S', 'PT4M4S',  'PT3M25S', 'PT3M48S', 'PT3M1S', 'PT4H3M1S',
                  'PT5H1S', 'PT5H', 'PT1M', 'PT3S', 'PT4H1M', 'PT']
    for duration in durations:
        h, m, s = split_duration(duration)
        print(h, m, s)
