import React from 'react';
import { useParams } from 'react-router-dom';
import { useSearch } from '../hooks/useSearch';
import { SearchInput } from '../components/search/SearchInput';
import { AiAnswerBlock } from '../components/search/AiAnswerBlock';
import { SourceCard } from '../components/search/SourceCard';
import { SuggestedQuestions } from '../components/search/SuggestedQuestions';

export const SearchPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const { search, isSearching, results } = useSearch(projectId);

  return (
    <div className="max-w-5xl mx-auto py-8 animate-in fade-in duration-300">
      <div className="text-center mb-10">
        <h2 className="text-3xl font-bold text-primary mb-3">Semantic Literature Search</h2>
        <p className="text-lg text-secondary">Ask complex questions. Get evidence-backed answers synthesized from your project papers.</p>
      </div>

      <SearchInput onSearch={search} isLoading={isSearching} />
      
      {!results && !isSearching && (
        <SuggestedQuestions onSelect={search} />
      )}

      {results && !isSearching && (
        <div className="mt-12 space-y-8 animate-in slide-in-from-bottom-4 duration-500">
          <AiAnswerBlock answer={results.answer} />
          
          <div>
            <h3 className="text-xl font-bold text-primary mb-4">Evidence Sources</h3>
            <div className="grid md:grid-cols-2 gap-4">
              {results.sources.map((source: any) => (
                <SourceCard key={source.id} source={source} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};