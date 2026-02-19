import { useState, useEffect } from 'react';
import './index.css';

const API_BASE = "https://plenty-tools-strive.loca.lt"

function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [url, setUrl] = useState("");
  const [sortBy, setSortBy] = useState("");

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/?sort_by=${sortBy}`);
      const data = await res.json();
      setProducts(data);
    } catch (error) {
      console.error("Fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  const startParsing = async () => {
    if (!url) return alert("Please paste an Amazon URL!");
    setParsing(true);
    try {
      const res = await fetch(`${API_BASE}/parse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category_url: url })
      });
      const data = await res.json();
      alert(data.detail);
      fetchProducts();
    } catch (e) {
      alert("Error starting parser");
    } finally {
      setParsing(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [sortBy]);

  // Хелпер для красивого отображения символа валюты
  const getCurrencySymbol = (currency) => {
    const symbols = { 'USD': '$', 'EUR': '€', 'GBP': '£', 'UAH': '₴' };
    return symbols[currency] || currency || '$';
  };

  return (
    <div className="min-h-screen bg-[#EAEDED] text-[#0F1111] font-sans selection:bg-[#febd69]/30">
      
      {/* Amazon Dark Nav Bar */}
      <nav className="bg-[#131921] px-4 py-3 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center gap-4">
          <div className="flex items-center gap-1 cursor-pointer">
            <span className="text-white text-2xl font-bold tracking-tight">amazon</span>
            <span className="text-[#febd69] text-sm font-bold pt-2">.parser</span>
          </div>

          <div className="flex-1 flex w-full shadow-sm">
            <input 
              type="text" 
              placeholder="Paste Amazon category URL here..." 
              className="w-full p-2.5 rounded-l-md outline-none focus:ring-2 focus:ring-[#febd69] transition-all"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
            <button 
              onClick={startParsing}
              disabled={parsing}
              className="bg-[#febd69] hover:bg-[#f3a847] transition-colors px-6 rounded-r-md flex items-center justify-center"
            >
              {parsing ? (
                <div className="w-5 h-5 border-2 border-[#131921] border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <svg className="w-6 h-6 text-[#131921]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              )}
            </button>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-white text-xs font-bold whitespace-nowrap">Sort by:</span>
            <select 
              className="bg-[#232f3e] text-white text-sm border border-gray-600 rounded p-1.5 outline-none focus:border-[#febd69] cursor-pointer"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="">Default</option>
              <option value="price">Price: Low to High</option>
              <option value="-price">Price: High to Low</option>
              <option value="rating">Avg. Customer Review</option>
            </select>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <h2 className="text-xl font-bold mb-6 pb-2 border-b border-gray-300">
          Best Sellers in Category <span className="text-gray-500 font-normal text-sm ml-2">({products.length} items found)</span>
        </h2>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 text-gray-500">
            <div className="w-10 h-10 border-4 border-[#febd69] border-t-transparent rounded-full animate-spin mb-4"></div>
            <p className="font-medium">Syncing with Amazon database...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {products.map((p) => (
              <div key={p.asin} className="bg-white p-4 border border-gray-200 flex flex-col hover:shadow-lg transition-all cursor-pointer group">
                
                <div className="h-56 relative mb-4 flex items-center justify-center overflow-hidden">
                  <img src={p.main_image_url} alt={p.title} className="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform duration-300" />
                  <div className="absolute top-0 left-0 bg-[#e47911] text-white text-[10px] font-bold px-2 py-0.5 shadow-sm">
                    # {p.rank} Best Seller
                  </div>
                </div>

                <div className="flex flex-col flex-1">
                  <h3 className="text-[#007185] group-hover:text-[#c45500] group-hover:underline text-sm font-medium line-clamp-3 mb-2 leading-tight">
                    {p.title}
                  </h3>

                  <div className="flex items-center gap-1 mb-1">
                    <span className="text-[#DE7921] font-bold text-sm">{p.rating || '0.0'}</span>
                    <div className="flex text-[#FFA41C] text-xs">
                        {"★".repeat(Math.floor(p.rating || 0))}${"☆".repeat(5 - Math.floor(p.rating || 0))}$
                    </div>
                    <span className="text-[#007185] text-xs ml-1">{p.reviews_count}</span>
                  </div>

                  {p.is_prime && (
                    <div className="mb-2">
                      <span className="bg-[#00A8E1] text-white text-[9px] font-black px-1.5 py-0.5 rounded-sm">✓prime</span>
                    </div>
                  )}

                  {/* Финальный блок цены с валютой */}
                  <div className="mt-auto pt-2">
                    <div className="flex items-start text-[#0F1111]">
                      <span className="text-xs font-medium pt-1 mr-0.5">
                        {getCurrencySymbol(p.currency)}
                      </span>
                      <span className="text-2xl font-medium leading-none">
                        {Math.floor(p.price || 0)}
                      </span>
                      <span className="text-xs font-medium pt-0.5">
                        {(p.price % 1).toFixed(2).substring(2)}
                      </span>
                    </div>
                    {p.list_price && (
                      <p className="text-xs text-[#565959] mt-0.5">
                        Typical: <span className="line-through">{getCurrencySymbol(p.currency)}{p.list_price}</span>
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <footer className="mt-20 border-t border-gray-300 bg-white py-12 text-center">
        <p className="text-xs text-gray-500">© 2026, Amazon Tracker | Developed by Vitalii Musiienko</p>
      </footer>
    </div>
  );
}

export default App;