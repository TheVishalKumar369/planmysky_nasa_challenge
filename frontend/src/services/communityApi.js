/**
 * Community API Service
 * Handles all community hub API calls (messages and reactions)
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Get community messages with pagination
 * @param {number} limit - Maximum number of messages to return
 * @param {number} skip - Number of messages to skip
 * @param {string} locationFilter - Optional location filter
 * @returns {Promise<Array>} Array of messages
 */
export const getMessages = async (limit = 20, skip = 0, locationFilter = null) => {
  try {
    const params = { limit, skip };
    if (locationFilter) {
      params.location_filter = locationFilter;
    }

    const response = await axios.get(`${API_BASE_URL}/api/community/messages`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching messages:', error);
    throw error;
  }
};

/**
 * Create a new community message
 * @param {Object} messageData - Message data
 * @param {string} messageData.username - Username of the poster
 * @param {string} messageData.location - Location of the user
 * @param {string} messageData.text - Message content
 * @param {number} messageData.latitude - Optional latitude
 * @param {number} messageData.longitude - Optional longitude
 * @returns {Promise<Object>} Created message response
 */
export const createMessage = async (messageData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/community/messages`, messageData);
    return response.data;
  } catch (error) {
    console.error('Error creating message:', error);
    throw error;
  }
};

/**
 * Add or update a reaction to a message
 * @param {string} messageId - ID of the message
 * @param {string} reactionType - Type of reaction (like, sun, rain, wind)
 * @param {string} userIdentifier - Unique user identifier
 * @returns {Promise<Object>} Reaction response
 */
export const updateReaction = async (messageId, reactionType, userIdentifier) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/community/reactions`, {
      message_id: messageId,
      reaction_type: reactionType,
      user_identifier: userIdentifier
    });
    return response.data;
  } catch (error) {
    console.error('Error updating reaction:', error);
    throw error;
  }
};

/**
 * Get a specific message by ID
 * @param {string} messageId - Message ID
 * @returns {Promise<Object>} Message object
 */
export const getMessage = async (messageId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/community/messages/${messageId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching message:', error);
    throw error;
  }
};

/**
 * Delete a message (only creator can delete)
 * @param {string} messageId - Message ID
 * @param {string} userIdentifier - Username or session ID of creator
 * @returns {Promise<Object>} Delete response
 */
export const deleteMessage = async (messageId, userIdentifier) => {
  try {
    const response = await axios.delete(
      `${API_BASE_URL}/api/community/messages/${messageId}`,
      { params: { user_identifier: userIdentifier } }
    );
    return response.data;
  } catch (error) {
    console.error('Error deleting message:', error);
    throw error;
  }
};

/**
 * Get community statistics
 * @returns {Promise<Object>} Community stats
 */
export const getCommunityStats = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/community/stats`);
    return response.data;
  } catch (error) {
    console.error('Error fetching community stats:', error);
    throw error;
  }
};
