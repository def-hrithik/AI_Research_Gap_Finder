import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../common/Button';

export const ClosingCta: React.FC = () => {
  return (
    <section className="py-24 px-6 border-t border-border">
      <div className="max-w-4xl mx-auto bg-accent text-white rounded-[2rem] p-12 md:p-20 text-center shadow-lg relative overflow-hidden">
        <div className="absolute inset-0 bg-white/5 opacity-50 blur-2xl rounded-full translate-x-1/2 -translate-y-1/2"></div>
        <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-6 relative z-10">Stop summarizing. <br/> Start discovering.</h2>
        <p className="text-accent-hover text-white/80 text-lg mb-10 max-w-2xl mx-auto relative z-10">
          Join thousands of researchers uncovering the next big breakthrough hidden in their existing literature library.
        </p>
        <Link to="/dashboard" className="relative z-10">
          <Button variant="secondary" size="lg" className="rounded-full text-primary border-none shadow-md px-8">
            Enter Workspace
          </Button>
        </Link>
      </div>
    </section>
  );
};