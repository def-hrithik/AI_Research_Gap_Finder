import React from 'react';
import { NavBar } from '../components/landing/NavBar';
import { Hero } from '../components/landing/Hero';
import { ExampleCarousel } from '../components/landing/ExampleCarousel';
import { ProblemSection } from '../components/landing/ProblemSection';
import { HowItWorks } from '../components/landing/HowItWorks';
import { FeatureGrid } from '../components/landing/FeatureGrid';
import { Testimonials } from '../components/landing/Testimonials';
import { Faq } from '../components/landing/Faq';
import { ClosingCta } from '../components/landing/ClosingCta';
import { Footer } from '../components/landing/Footer';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-background text-primary selection:bg-accent/30 flex flex-col">
      <NavBar />
      <main className="flex-1">
        <Hero />
        <ExampleCarousel />
        <ProblemSection />
        <HowItWorks />
        <FeatureGrid />
        <Testimonials />
        <Faq />
        <ClosingCta />
      </main>
      <Footer />
    </div>
  );
};