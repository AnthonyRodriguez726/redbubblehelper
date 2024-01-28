from flask import request, jsonify
from datetime import datetime, timedelta
from BingImageCreator import ImageGen
import search_info
import logging
import pytz


logging.basicConfig(level=logging.DEBUG, filename='debug.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

def register_api_routes(app):
    @app.route('/generate_design', methods=['POST'])
    def generate_design():
        data = request.get_json()
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        design_url = search_info.generate_design(prompt)
        if design_url:
            return jsonify({"design_url": design_url})
        else:
            return jsonify({"error": "Failed to generate design"}), 500


    @app.route('/search', methods=['GET'])
    def search():
        cst_timezone = pytz.timezone('America/Chicago')  # CST timezone
        current_time_cst = datetime.now(cst_timezone).strftime('%Y-%m-%d %I:%M:%S %p')

        query = request.args.get('query')
        if not query:
            return jsonify({"error": "No query provided"}), 400

        logging.debug(f"Searching Redbubble for {query} - {current_time_cst}")
        try:
            # Use the scraper to get the results
            results = search_info.search_redbubble(query)
            return jsonify({"results": results})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route('/multi_search', methods=['POST'])
    def multi_search():
        cst_timezone = pytz.timezone('America/Chicago')  # CST timezone
        current_time_cst = datetime.now(cst_timezone).strftime('%Y-%m-%d %I:%M:%S %p')
        data = request.get_json()
        if not data or 'searches' not in data:
            return jsonify({"error": "No searches provided"}), 400

        logging.debug(f"Starting Redbubble Multi Search at {current_time_cst}")
        results = {}
        for search in data['searches']:
            query = search.get('query')
            media_type = search.get('media_type', 'unknown')  # Default to 'unknown' if not provided
            if query:
                try:
                    # Use the scraper to get results and URL for each query
                    search_result, search_url = search_info.search_redbubble(query)
                    results[query] = {
                        'result': search_result,
                        'url': search_url,
                        'media_type': media_type  # Include the media type in the response
                    }
                except Exception as e:
                    results[query] = {"error": f"An error occurred: {str(e)}"}
            else:
                results[query] = {"error": "Missing query"}

        return jsonify(results)


    @app.route('/toptv', methods=['GET'])
    def top_tv_shows():

        try:
            # Use the scraper to get the results
            results = search_info.find_top_tv_shows()
            return jsonify({"results": results})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route('/topmedia', methods=['GET'])
    def top_media():

        try:
            # Use the scraper to get the results
            results = search_info.find_top_media()
            return jsonify({"results": results})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route('/generate_design', methods=['POST'])
    def bing_generate_design():
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        # Directly use the original prompt for design generation
        image_links = generate_design(prompt)
        if image_links:
            return jsonify({"images": image_links})
        else:
            return jsonify({"error": "Failed to generate images"}), 500