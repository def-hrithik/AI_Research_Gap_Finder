import React, { useState } from 'react';
import { Search as SearchIcon, ArrowRight } from 'lucide-react';
import { Button } from '../common/Button';

interface SearchInputProps {
  onSearch: (query: string) => void;
  isLoading?: boolean;
}

export const SearchInput: React.FC<SearchInputProps> = ({ onSearch, isLoading }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) onSearch(query);
  };

  return (
    <form onSubmit={handleSubmit} className="relative flex items-center w-full max-w-4xl mx-auto">
      <div className="absolute left-6 text-secondary">
        <SearchIcon size={24} />
      </div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question about the literature... (e.g., What are the common limitations?)"
        className="w-full pl-16 pr-32 py-5 rounded-2xl border-2 border-border bg-surface text-lg focus:outline-none focus:ring-4 focus:ring-accent/20 focus:border-accent text-primary shadow-sm transition-all"
        disabled={isLoading}
      />
      <div className="absolute right-3">
        <Button type="submit" disabled={!query.trim() || isLoading} className="rounded-xl px-6 h-12">
          {isLoading ? 'Searching...' : <><span className="mr-2">Ask AI</span> <ArrowRight size={18} /></>}
        </Button>
      </div>
    </form>
  );
};