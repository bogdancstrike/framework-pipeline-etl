from flask import Flask, jsonify, request
from flask_cors import CORS
from models import ConsumerConfig, create_session, init_db
from sqlalchemy.orm import scoped_session, sessionmaker
from utils.logger import logger

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and allow all origins

# Initialize the database
init_db()

# Create a scoped session
Session = scoped_session(sessionmaker(bind=create_session().bind))


@app.route('/api/consumer_configs', methods=['GET'])
def get_consumer_configs():
    session = Session()
    try:
        logger.debug("GET /api/consumer_configs called")
        configs = session.query(ConsumerConfig).all()
        result = [
            {
                "id": config.id,
                "consumer_name": config.consumer_name,
                "topics_input": config.topics_input,
                "topics_output": config.topics_output,
                "metadatas": config.metadatas,
                "kafka_bootstrap_server": config.kafka_bootstrap_server,
                "timeout": config.timeout  # Include timeout
            } for config in configs
        ]
        logger.info(f"Successfully retrieved {len(result)} consumer configs.")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error retrieving consumer configs: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route('/api/consumer_configs', methods=['POST'])
def update_consumer_configs():
    session = Session()
    try:
        configs = request.json  # Get JSON from the request
        logger.debug(f"POST /api/consumer_configs called with data: {configs}")

        # Clear existing data
        session.query(ConsumerConfig).delete()
        logger.info("Existing consumer configs cleared.")

        # Insert new data
        for config in configs:
            new_config = ConsumerConfig(
                consumer_name=config['worker_name'],
                topics_input=config['topics_input'],
                topics_output=config['topics_output'],
                metadatas=config.get('metadatas'),
                kafka_bootstrap_server=config.get('kafka_bootstrap_server', "localhost:9092"),  # Get default if missing
                timeout=config.get('timeout')  # Include timeout
            )
            session.add(new_config)

        session.commit()
        logger.info("Consumer configs updated successfully.")
        return jsonify({"message": "Consumer configs updated successfully."}), 200
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating consumer configs: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 Not Found: {request.url}")
    return jsonify({"error": "Not found"}), 404


if __name__ == '__main__':
    logger.info("Starting Flask app...")
    app.run(debug=True)
