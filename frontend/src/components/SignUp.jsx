import { useState, useContext } from "react";
import { AuthContext } from "../contexts/AuthContext";
import { signup } from "../services/authApi";

export default function Signup({ onSuccess }) {
  const { login: setAuthToken } = useContext(AuthContext);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleSignup = async (e) => {
    e.preventDefault();
    const data = await signup(email, password);
    if (data.token) {
      setAuthToken(data.token); // log in user immediately
      setMessage("Signup successful!");
      setEmail(""); 
      setPassword("");
      if (onSuccess) onSuccess();
    } else {
      setMessage(data.detail || "Signup failed");
    }
  };

  return (
    <form onSubmit={handleSignup}>
      <h2>Sign Up</h2>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      <button type="submit">Sign Up</button>
      <p>{message}</p>
    </form>
  );
}
