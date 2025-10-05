
import React, { useState } from "react";
import dummyPosts from "../data/dummyPosts.json";

const MiniPosts = () => {
  const [visibleCount, setVisibleCount] = useState(3); // show 3 posts initially
  const [posts] = useState(dummyPosts);

  const showMorePosts = () => {
    if (visibleCount >= posts.length) {
      // collapse if all posts are visible
      setVisibleCount(3);
    } else {
      // show 3 more
      setVisibleCount((prev) => prev + 3);
    }
  };

  const isAllVisible = visibleCount >= posts.length;

  return (
    <div className="mini-posts">
      <h3>🌍 Community Status Updates</h3>

      {posts.slice(0, visibleCount).map((post) => (
        <div key={post.id} className="post-card">
          <p>
            <strong>{post.username}</strong> • {post.location}
          </p>
          <p>{post.text}</p>
          <small>{post.timestamp}</small>

          <div className="reactions">
            <button>👍 {post.reactions.like}</button>
            <button>☀️ {post.reactions.sun}</button>
            <button>🌧 {post.reactions.rain}</button>
            <button>💨 {post.reactions.wind}</button>
          </div>
        </div>
      ))}

      <button className="see-more-btn" onClick={showMorePosts}>
        {isAllVisible ? "View Less Posts" : "View More Posts"}
      </button>
    </div>
  );
};

export default MiniPosts;

