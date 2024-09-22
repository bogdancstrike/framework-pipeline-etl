import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

export const fetchConsumerConfigs = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/consumer_configs`);
        return response.data;
    } catch (error) {
        console.error('Error fetching consumer configs:', error);
        throw error;
    }
};

export const updateConsumerConfigs = async (data) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/consumer_configs`, data);
        return response.data;
    } catch (error) {
        console.error('Error updating consumer configs:', error);
        throw error;
    }
};
