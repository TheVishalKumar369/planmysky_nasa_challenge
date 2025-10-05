import React, { useState, useEffect } from "react";
import { getMessages, createMessage, updateReaction, deleteMessage } from "../services/communityApi";

const MiniPosts = () => {
  const [visibleCount, setVisibleCount] = useState(3);
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showNewPostForm, setShowNewPostForm] = useState(false);
  const [newPost, setNewPost] = useState({
    username: '',
    location: '',
    text: ''
  });
  const [userIdentifier, setUserIdentifier] = useState('');

  // Get or create user identifier (for tracking reactions and posts)
  useEffect(() => {
    let identifier = localStorage.getItem('community_user_id');
    if (!identifier) {
      identifier = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('community_user_id', identifier);
    }
    setUserIdentifier(identifier);
  }, []);

  // Load messages on component mount
  useEffect(() => {
    loadMessages();
  }, []);

  const loadMessages = async () => {
    try {
      setLoading(true);
      const messages = await getMessages(50, 0);
      setPosts(messages);
      setError(null);
    } catch (err) {
      setError('Failed to load messages. Please try again later.');
      console.error('Error loading messages:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePostSubmit = async (e) => {
    e.preventDefault();

    if (!newPost.username || !newPost.location || !newPost.text) {
      alert('Please fill in all fields');
      return;
    }

    try {
      // Save username to localStorage for future posts
      localStorage.setItem('community_username', newPost.username);
      localStorage.setItem('community_location', newPost.location);

      await createMessage({
        username: newPost.username,
        location: newPost.location,
        text: newPost.text
      });

      // Reset form
      setNewPost({ username: '', location: '', text: '' });
      setShowNewPostForm(false);

      // Reload messages
      await loadMessages();
    } catch (err) {
      alert('Failed to post message. Please try again.');
      console.error('Error creating message:', err);
    }
  };

  const handleReaction = async (messageId, reactionType) => {
    if (!userIdentifier) return;

    try {
      await updateReaction(messageId, reactionType, userIdentifier);

      // Reload messages to get updated reaction counts
      await loadMessages();
    } catch (err) {
      console.error('Error updating reaction:', err);
    }
  };

  const handleDeletePost = async (messageId, messageUsername) => {
    const savedUsername = localStorage.getItem('community_username');

    if (savedUsername !== messageUsername) {
      alert('You can only delete your own posts');
      return;
    }

    if (!confirm('Are you sure you want to delete this post?')) {
      return;
    }

    try {
      await deleteMessage(messageId, savedUsername);
      await loadMessages();
    } catch (err) {
      alert('Failed to delete post. You may not have permission.');
      console.error('Error deleting message:', err);
    }
  };

  const showMorePosts = () => {
    if (visibleCount >= posts.length) {
      setVisibleCount(3);
    } else {
      setVisibleCount((prev) => prev + 3);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const isAllVisible = visibleCount >= posts.length;

  // Auto-fill username and location from localStorage
  useEffect(() => {
    const savedUsername = localStorage.getItem('community_username');
    const savedLocation = localStorage.getItem('community_location');

    if (savedUsername && savedLocation) {
      setNewPost(prev => ({
        ...prev,
        username: savedUsername,
        location: savedLocation
      }));
    }
  }, [showNewPostForm]);

  if (loading && posts.length === 0) {
    return (
      <div className="mini-posts">
        <h3>🌍 Community Status Updates</h3>
        <p style={{ textAlign: 'center', padding: '20px' }}>Loading messages...</p>
      </div>
    );
  }

  return (
    <div className="mini-posts">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3>🌍 Community Status Updates</h3>
        <button
          className="new-post-btn"
          onClick={() => setShowNewPostForm(!showNewPostForm)}
          style={{
            background: '#4CAF50',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          {showNewPostForm ? '✕ Cancel' : '+ New Post'}
        </button>
      </div>

      {error && (
        <div style={{
          background: '#ffebee',
          color: '#c62828',
          padding: '10px',
          borderRadius: '4px',
          marginBottom: '10px'
        }}>
          {error}
        </div>
      )}

      {showNewPostForm && (
        <form onSubmit={handlePostSubmit} className="new-post-form" style={{
          background: '#f5f5f5',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '15px'
        }}>
          <input
            type="text"
            placeholder="Your name"
            value={newPost.username}
            onChange={(e) => setNewPost({ ...newPost, username: e.target.value })}
            maxLength={50}
            style={{
              width: '100%',
              padding: '8px',
              marginBottom: '8px',
              borderRadius: '4px',
              border: '1px solid #ddd'
            }}
            required
          />
          <input
            type="text"
            placeholder="Your location (e.g., Kathmandu, Nepal)"
            value={newPost.location}
            onChange={(e) => setNewPost({ ...newPost, location: e.target.value })}
            maxLength={100}
            style={{
              width: '100%',
              padding: '8px',
              marginBottom: '8px',
              borderRadius: '4px',
              border: '1px solid #ddd'
            }}
            required
          />
          <textarea
            placeholder="Share your weather experience..."
            value={newPost.text}
            onChange={(e) => setNewPost({ ...newPost, text: e.target.value })}
            maxLength={500}
            rows={3}
            style={{
              width: '100%',
              padding: '8px',
              marginBottom: '8px',
              borderRadius: '4px',
              border: '1px solid #ddd',
              resize: 'vertical'
            }}
            required
          />
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <button
              type="submit"
              style={{
                background: '#2196F3',
                color: 'white',
                border: 'none',
                padding: '8px 20px',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Post Message
            </button>
          </div>
        </form>
      )}

      {posts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
          <p>No messages yet. Be the first to share!</p>
        </div>
      ) : (
        <>
          {posts.slice(0, visibleCount).map((post) => (
            <div key={post.id} className="post-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div>
                  <p>
                    <strong>{post.username}</strong> • {post.location}
                  </p>
                </div>
                {localStorage.getItem('community_username') === post.username && (
                  <button
                    onClick={() => handleDeletePost(post.id, post.username)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: '#999',
                      cursor: 'pointer',
                      fontSize: '18px',
                      padding: '0 5px'
                    }}
                    title="Delete post"
                  >
                    🗑️
                  </button>
                )}
              </div>
              <p>{post.text}</p>
              <small>{formatTimestamp(post.timestamp)}</small>

              <div className="reactions">
                <button onClick={() => handleReaction(post.id, 'like')}>
                  👍 {post.reactions.like}
                </button>
                <button onClick={() => handleReaction(post.id, 'sun')}>
                  ☀️ {post.reactions.sun}
                </button>
                <button onClick={() => handleReaction(post.id, 'rain')}>
                  🌧 {post.reactions.rain}
                </button>
                <button onClick={() => handleReaction(post.id, 'wind')}>
                  💨 {post.reactions.wind}
                </button>
              </div>
            </div>
          ))}

          {posts.length > 3 && (
            <button className="see-more-btn" onClick={showMorePosts}>
              {isAllVisible ? "View Less Posts" : "View More Posts"}
            </button>
          )}
        </>
      )}
    </div>
  );
};

export default MiniPosts;
