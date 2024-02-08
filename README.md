# Redbubble Helper
**Sign up for updates about our Website, API, and Custom GPT here! https://redbubblehelper.com/**

## Description

Redbubble Helper is a web application designed to enhance the productivity of Redbubble artists. It integrates a custom-built API with a GPT-4 powered assistant, enabling users to automate various tasks, access detailed insights, and edit designs without the need for image editing software. This tool aims to streamline the workflow for artists, making it easier to research niches, manage portfolios, and optimize listings.

## Installation

Follow these steps to set up Redbubble Helper on your local machine:

```bash
git clone https://github.com/AnthonyRodriguez726/redbubblehelper.git
cd redbubblehelper
# Install dependencies (it's ideal to create a virtual environment and activate it before continuing to the next steps)
pip install -r requirements.txt
# Run the application
python main.py
```

## Usage

After launching Redbubble Helper, visit `http://localhost:5000` to access the web interface.

*Visit `http://localhost:5000/features` to access the in-progress website.*

*Usage examples coming soon!*

## Example API Calls

### Search Endpoint

Shows you the amount of search results for a given query on Redbubble to give you a better understanding of whether or not a niche is already over-saturated.

**Request:**
`GET /api/search?query=<your-search-query>`
Replace `<your-search-query>` with the actual search term you're interested in, such as "minimalist nature".

**Example:**
`GET /api/search?query=minimalist nature`

**Response:**
*200 - successful operation*
```
{
  "results": [
    "36,887 Results",
    "https://www.redbubble.com/shop/?query=minimalist%20nature"
  ]
}
```

### Top Media Endpoint

Retrieve top media items across different categories. This endpoint includes media that is currently popular as well as media that is expected to be popular in the near future. (Types of media currently include movies, tv shows, books, anime, and video games)

**Request:**
`GET /api/topmedia`
No additional parameters are required for this endpoint.

**Response:**
*200 - sucessful operation (this endpoint will usually return 20 results)*
```
{
	  "results": [
	    {
	      "href": "https://www.rottentomatoes.com/tv/hazbin_hotel/s01",
	      "media_type": "tv show",
	      "title": "Hazbin Hotel: Season 1"
	    },
	    {
	      "href": "https://myanimelist.net/anime/56524/Tunshi_Xingkong_4th_Season",
	      "media_type": "anime",
	      "title": "Tunshi Xingkong 4th Season"
	    },
	    {
	      "href": "https://www.goodreads.com/book/show/52381770-network-effect",
	      "media_type": "book",
	      "title": "Network Effect (The Murderbot Diaries, #5)"
	    }
	]
}
```


## Features

*Features list + examples coming soon!*

## Contributing


1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/NewFeature`)
3. Commit your Changes (`git commit -m 'Added new feature'`)
4. Push to the Branch (`git push origin feature/NewFeature`)
5. Open a Pull Request


## Contact

If you have any questions, concerns, or issues, feel free to email me at *anthonyrodriguez726@gmail.com*