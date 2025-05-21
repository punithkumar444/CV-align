import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import SignUp from './pages/SignUp';

function App() {
  return (
    <AuthProvider>
      <Navbar />
      <Routes>
        {/* We'll fill these in later */}
        <Route path="/" element={<div>Home</div>} />
        <Route path="/signin" element={<div>Sign In</div>} />
        <Route path="/signup" element={<SignUp />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
