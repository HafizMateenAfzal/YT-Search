import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyBF_mH8qXyz4BSqx4kQivMv_YD6_Fq7-bQ"  # Replace this with your actual YouTube API key
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Topic Explorer Tool")

# Input Fields for Keywords, Location, and Days
keywords = st.text_input("Enter Keywords (comma-separated):", "sports, football, basketball")
location = st.text_input("Enter Location (country code, e.g., US for United States):", "US")
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=7)

# Button to fetch data
if st.button("Fetch Data"):
    try:
        # Calculate the date range based on the number of days entered
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        # Prepare the list of keywords by splitting them by commas
        keyword_list = [keyword.strip() for keyword in keywords.split(",")]

        # Iterate over the list of keywords
        for keyword in keyword_list:
            st.write(f"Searching for keyword: {keyword}")

            # Define search parameters for the YouTube API
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "regionCode": location,  # Location filter (country code)
                "key": API_KEY,
            }

            # Make the API request to fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if response.status_code != 200 or "items" not in data:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]

            # Fetch video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data:
                st.warning(f"Failed to fetch video statistics for keyword: {keyword}")
                continue

            # Fetch channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data:
                st.warning(f"Failed to fetch channel statistics for keyword: {keyword}")
                continue

            stats = stats_data["items"]
            channels = channel_data["items"]

            # Collect the results (title, description, views, subscribers)
            for video, stat, channel in zip(videos, stats, channels):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                if subs < 3000:  # Only include channels with fewer than 3,000 subscribers
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })

        # Display results
        if all_results:
            st.success(f"Found {len(all_results)} results across all keywords!")
            for result in all_results:
                st.markdown(
                    f"**Title**: {result['Title']}\n"
                    f"**Description**: {result['Description']}\n"
                    f"**Views**: {result['Views']}\n"
                    f"**Subscribers**: {result['Subscribers']}\n"
                    f"[Watch Video]({result['URL']})\n"
                )
        else:
            st.warning("No results found based on your search criteria.")

    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
