import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles } from 'lucide-react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';

export const Hero: React.FC = () => {
  return (
    <section className="pt-40 pb-24 px-6 text-center max-w-5xl mx-auto flex flex-col items-center">
      <Badge variant="accent" className="mb-6 py-1 px-3">
        <Sparkles size={14} className="mr-2" /> AI-Powered Literature Synthesis
      </Badge>
      <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-primary leading-[1.1] mb-6">
        Discover What Research <br />
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-accent-hover">Hasn't Explored Yet.</span>
      </h1>
      <p className="text-lg md:text-xl text-secondary max-w-2xl mb-10 leading-relaxed">
        Upload your library. Let our semantic engine analyze the evidence to surface hidden contradictions, repeated limitations, and high-confidence candidate research gaps.
      </p>
      <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
        <Link to="/dashboard" className="w-full sm:w-auto">
          <Button size="lg" className="w-full sm:w-auto rounded-full gap-2 text-base shadow-md h-14 px-8">
            Start Discovering Gaps <ArrowRight size={18} />
          </Button>
        </Link>
        <Button variant="secondary" size="lg" className="w-full sm:w-auto rounded-full h-14 px-8">
          See How It Works
        </Button>
      </div>
    </section>
  );
};