import React from 'react';
import { Target, Globe, MessageSquare, Mail } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-surface border-t border-border py-12 px-6">
      <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
        <div className="col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-6 h-6 rounded-lg bg-accent flex items-center justify-center">
              <Target size={14} className="text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight">Nexus</span>
          </div>
          <p className="text-secondary text-sm max-w-sm mb-6">
            The premium research intelligence workspace for discovering what the literature has not explored yet.
          </p>
          <div className="flex gap-4 text-secondary">
            <Globe size={20} className="hover:text-primary cursor-pointer transition-colors" />
            <MessageSquare size={20} className="hover:text-primary cursor-pointer transition-colors" />
            <Mail size={20} className="hover:text-primary cursor-pointer transition-colors" />
          </div>
        </div>
        
        <div>
          <h4 className="font-bold mb-4">Product</h4>
          <ul className="space-y-2 text-sm text-secondary">
            <li><a href="#" className="hover:text-primary transition-colors">Features</a></li>
            <li><a href="#" className="hover:text-primary transition-colors">Pricing</a></li>
            <li><a href="#" className="hover:text-primary transition-colors">Security</a></li>
          </ul>
        </div>
        
        <div>
          <h4 className="font-bold mb-4">Company</h4>
          <ul className="space-y-2 text-sm text-secondary">
            <li><a href="#" className="hover:text-primary transition-colors">About</a></li>
            <li><a href="#" className="hover:text-primary transition-colors">Blog</a></li>
            <li><a href="#" className="hover:text-primary transition-colors">Contact</a></li>
          </ul>
        </div>
      </div>
      <div className="max-w-7xl mx-auto pt-8 border-t border-border text-sm text-secondary flex flex-col md:flex-row justify-between items-center gap-4">
        <p>© 2026 Nexus Research Intelligence. All rights reserved.</p>
        <div className="flex gap-4">
          <a href="#" className="hover:text-primary transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-primary transition-colors">Terms of Service</a>
        </div>
      </div>
    </footer>
  );
};