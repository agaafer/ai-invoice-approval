// App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import MasterPage from './pages/MasterPage';
import DetailsPage from './pages/DetailsPage';

function App() {
  return (
    
	<Router>
      <Routes>
        <Route path="/" element={<MasterPage />} />
        <Route path="/details/:id" element={<DetailsPage />} />
      </Routes>
    </Router>
  );
}

export default App;