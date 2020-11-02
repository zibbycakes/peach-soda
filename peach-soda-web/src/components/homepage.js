import React from 'react';
import Login from './login';

function Homepage() {
  return (
    <div className="App">
      <h1>Welcome to Peach Soda!</h1>
      <p>Use this website to view and suggest music themes for our weekly playlist.</p>
      <br></br>
      <Login />
    </div>
  );
}

export default Homepage;
