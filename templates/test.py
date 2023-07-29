from datetime import datetime

# Get the current time as a datetime object
current_time = datetime.now()

# Print the current time in the default format (including date and time)
print("Current time:", current_time)

# If you want to display only the time in a specific format
formatted_time = current_time.strftime("%H:%M:%S")  # 24-hour format with seconds
print("Formatted time:", formatted_time)
