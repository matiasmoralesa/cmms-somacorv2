import React from 'react';

interface NavLinkProps {
  icon?: React.ReactNode;
  label: string;
  onClick: () => void;
}

const NavLink: React.FC<NavLinkProps> = ({ icon, label, onClick }) => (
    <a 
        href="#" 
        onClick={(e) => {
            e.preventDefault();
            onClick();
        }} 
        className="flex items-center px-4 py-2 text-gray-300 rounded-md hover:bg-gray-700 hover:text-white transition-colors"
    >
        {icon}
        <span className="ml-3">{label}</span>
    </a>
);

export default NavLink;