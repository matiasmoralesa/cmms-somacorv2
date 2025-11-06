import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const NavGroup = ({ title, icon, children }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div>
            <button 
                onClick={() => setIsOpen(!isOpen)} 
                className="w-full flex justify-between items-center px-4 py-2 text-gray-300 rounded-md hover:bg-gray-700 hover:text-white transition-colors"
            >
                <span className="flex items-center">
                    {icon}
                    <span className="ml-3">{title}</span>
                </span>
                <ChevronDown 
                    size={16} 
                    className={`transition-transform transform ${isOpen ? 'rotate-180' : ''}`} 
                />
            </button>
            {isOpen && (
                <div className="pl-8 mt-1 space-y-1">
                    {children}
                </div>
            )}
        </div>
    );
};

export default NavGroup;