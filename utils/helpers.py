def format_time(seconds):
    """Convert seconds to mm:ss format"""
    if not seconds:
        return "00:00"
    
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{int(minutes):02d}:{int(seconds):02d}"
