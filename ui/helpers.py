def get_segment_color_class(segment: str) -> str:
    if segment == 'High':
        return 'high-value'
    elif segment == 'Medium':
        return 'medium-value'
    else:
        return 'low-value'


def get_retention_color_class(retention_rate: float) -> str:
    if retention_rate >= 0.7:
        return 'retention-high'
    elif retention_rate >= 0.4:
        return 'retention-medium'
    else:
        return 'retention-low'


