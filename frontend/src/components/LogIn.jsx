import { useState, useContext } from "react";
import { AuthContext } from "../contexts/AuthContext";
import { login as loginApi } from "../services/authApi";

export default function Login({ onSuccess }) {
  const { login: setAuthToken } = useContext(AuthContext);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    const data = await loginApi(email, password);
    if (data.token) {
      setAuthToken(data.token);
      setMessage("Login successful!");
      if (onSuccess) onSuccess();
    } else {
      setMessage(data.detail || "Login failed");
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <h2>Login</h2>
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
      <button type="submit">Log In</button>
      <p>{message}</p>
    </form>
  );
}

