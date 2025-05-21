import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav style={{ display: 'flex', gap: '1rem', padding: '1rem' }}>
      <Link to="/">Home</Link>
      {!user && (
        <>
          <Link to="/signin">Sign In</Link>
          <Link to="/signup">Sign Up</Link>
        </>
      )}
      {user && user.role === 'company' && (
        <>
          <Link to="/create-job">Create Job</Link>
          <Link to="/my-jobs">My Job Roles</Link>
        </>
      )}
      {user && user.role === 'user' && (
        <>
          <Link to="/apply-job">Apply for Job</Link>
        </>
      )}
      {user && <button onClick={handleLogout}>Logout</button>}
    </nav>
  );
};

export default Navbar;
