import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users, Coins, Info, BrainCircuit, BarChart3,
  PlayCircle, Home, User, Ghost, Smile,
  Star, Heart, Bird, Cat, Dog, Rabbit
} from 'lucide-react';
import axios from 'axios';
import { useSoundEffects } from './hooks/useSoundEffects';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const AVATARS = [
  { id: 0, icon: <User size={40} /> },
  { id: 1, icon: <Ghost size={40} /> },
  { id: 2, icon: <Smile size={40} /> },
  { id: 3, icon: <Star size={40} /> },
  { id: 4, icon: <Heart size={40} /> },
  { id: 5, icon: <Bird size={40} /> },
  { id: 6, icon: <Cat size={40} /> },
  { id: 7, icon: <Dog size={40} /> },
  { id: 8, icon: <Rabbit size={40} /> },
];

const DIFFICULTIES = [
  { id: 'easy', name: 'Легко', desc: 'Боты часто ошибаются' },
  { id: 'medium', name: 'Средне', desc: 'Сбалансированная игра' },
  { id: 'hard', name: 'Профи', desc: 'Минимум ошибок, агрессия' },
];

function App() {
  const [gameState, setGameState] = useState(null);
  const [playerCount, setPlayerCount] = useState(6);
  const [gameStarted, setGameStarted] = useState(false);
  const [raiseAmount, setRaiseAmount] = useState(100);
  const [loading, setLoading] = useState(false);
  const [scenario, setScenario] = useState('classic');
  const [difficulty, setDifficulty] = useState('medium');
  const [avatarId, setAvatarId] = useState(0);
  const [showStats, setShowStats] = useState(false);
  const [stats, setStats] = useState(null);

  const { playSound } = useSoundEffects();

  useEffect(() => {
    if (gameState?.phase === 'Вскрытие') {
      playSound('win');
    } else if (gameState?.phase) {
      playSound('deal');
    }
  }, [gameState?.phase]);

  useEffect(() => {
    const grade = gameState?.analysis?.grade;
    if (grade === 'Ошибка' || grade === 'Грубая ошибка') {
      playSound('alert');
    }
  }, [gameState?.analysis]);

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API_BASE}/stats`);
      setStats(res.data);
    } catch (err) {
      console.error("Failed to fetch stats", err);
    }
  };

  useEffect(() => {
    if (showStats) fetchStats();
  }, [showStats]);

  const startGame = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/start`, {
        player_count: playerCount,
        starting_stack: 1000,
        scenario: scenario,
        difficulty: difficulty,
        avatar_id: avatarId
      });
      setGameState(res.data);
      setGameStarted(true);
      setShowStats(false);
    } catch (err) {
      alert("Ошибка подключения к бэкенду. Пожалуйста, попробуйте позже или проверьте соединение.");
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action, amount = 0) => {
    setLoading(true);
    if (action !== 'fold') playSound('chips');
    try {
      const res = await axios.post(`${API_BASE}/action`, {
        action,
        amount: parseInt(amount)
      });
      setGameState(res.data);
    } catch (err) {
      console.error("Действие не удалось", err);
    } finally {
      setLoading(false);
    }
  };

  const scenarios = [
    { id: 'classic', name: 'Классика', desc: '100 BB, обычная игра' },
    { id: 'short_stack', name: 'Короткий стек', desc: '15 BB, агрессивная игра' },
    { id: 'bubble', name: 'Баббл', desc: 'Высокие блайнды, осторожные боты' },
    { id: 'final_table', name: 'Финальный стол', desc: 'Максимальное давление' },
  ];

  if (showStats) {
    return (
      <div className="flex flex-col items-center justify-center h-screen space-y-8 bg-slate-950 text-white p-4">
        <h2 className="text-4xl font-black text-yellow-500 uppercase tracking-tighter">ВАША СТАТИСТИКА</h2>
        <div className="grid grid-cols-2 gap-4 w-full max-w-2xl">
          <StatCard label="Раздач сыграно" value={stats?.total_hands || 0} />
          <StatCard label="VPIP %" value={`${stats?.vpip || 0}%`} sub="Вход в банк" />
          <StatCard label="PFR %" value={`${stats?.pfr || 0}%`} sub="Рейз префлоп" />
          <StatCard label="Win Rate" value={`${stats?.win_rate || 0}%`} />
          <StatCard label="Прибыль" value={stats?.profit || 0} color={stats?.profit >= 0 ? 'text-green-500' : 'text-red-500'} />
          <StatCard label="Ошибок всего" value={stats?.errors || 0} color="text-orange-500" />
        </div>

        {stats?.error_log?.length > 0 && (
          <div className="w-full max-w-2xl space-y-4">
            <h3 className="text-xl font-bold text-slate-400 uppercase tracking-widest">Последние ошибки</h3>
            <div className="space-y-2">
              {stats.error_log.map((err, i) => (
                <div key={i} className="bg-red-500/10 border border-red-500/20 p-4 rounded-2xl">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-red-400 font-bold uppercase text-xs">{err.verdict}</span>
                    <span className="text-slate-500 text-[10px]">{err.timestamp}</span>
                  </div>
                  <p className="text-sm text-slate-300">{err.comment}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <button onClick={() => setShowStats(false)} className="bg-slate-800 hover:bg-slate-700 p-4 px-8 rounded-2xl font-bold flex items-center transition-all active:scale-95">
          <Home className="mr-2" /> НАЗАД В МЕНЮ
        </button>
      </div>
    );
  }

  if (!gameStarted) {
    return (
      <div className="flex flex-col items-center justify-center h-screen space-y-8 bg-slate-950 text-white overflow-y-auto py-10 px-4">
        <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="text-center">
          <h1 className="text-5xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-600 mb-2 leading-none">
            ПОКЕРНЫЙ ТРЕНЕР
          </h1>
          <p className="text-slate-400 tracking-widest uppercase text-xs md:text-sm">Профессиональный симулятор турниров</p>
        </motion.div>

        <div className="bg-slate-900 p-6 md:p-10 rounded-[32px] shadow-2xl border border-slate-800 w-full max-w-[800px] backdrop-blur-xl bg-opacity-80 space-y-8">
          <div className="flex justify-center border-b border-slate-800 pb-6">
            <button onClick={() => setShowStats(true)} className="flex flex-col items-center text-slate-400 hover:text-white transition-colors group">
              <div className="p-3 rounded-full bg-slate-800 group-hover:bg-slate-700 mb-2 transition-all"><BarChart3 size={24} /></div>
              <span className="text-[10px] uppercase font-black tracking-widest">Статистика</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Левая колонка - Сценарии и Игроки */}
            <div className="space-y-6">
              <div className="space-y-4">
                <label className="block text-slate-400 text-[10px] font-black uppercase tracking-widest">Сценарий</label>
                <div className="grid grid-cols-2 gap-2">
                  {scenarios.map(s => (
                    <button key={s.id} onClick={() => setScenario(s.id)} className={`p-3 rounded-xl border transition-all text-left ${scenario === s.id ? 'bg-yellow-500/10 border-yellow-500 text-yellow-500' : 'bg-slate-950/20 border-slate-800 text-slate-500 hover:border-slate-700'}`}>
                      <div className="text-xs font-bold">{s.name}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <label className="block text-slate-400 text-[10px] font-black uppercase tracking-widest">Сложность ботов</label>
                <div className="grid grid-cols-3 gap-2">
                  {DIFFICULTIES.map(d => (
                    <button key={d.id} onClick={() => setDifficulty(d.id)} className={`p-2 rounded-xl border transition-all text-center ${difficulty === d.id ? 'bg-blue-500/10 border-blue-500 text-blue-400' : 'bg-slate-950/20 border-slate-800 text-slate-500 hover:border-slate-700'}`}>
                      <div className="text-[10px] font-black uppercase">{d.name}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Правая колонка - Аватар и Игроки */}
            <div className="space-y-6">
              <div className="space-y-4">
                <label className="block text-slate-400 text-[10px] font-black uppercase tracking-widest">Ваш аватар</label>
                <div className="grid grid-cols-5 gap-2">
                  {AVATARS.map(a => (
                    <button key={a.id} onClick={() => setAvatarId(a.id)} className={`w-10 h-10 flex items-center justify-center rounded-full transition-all border-2 ${avatarId === a.id ? 'bg-yellow-500 text-black border-white' : 'bg-slate-800 text-slate-500 border-transparent hover:bg-slate-700'}`}>
                      {React.cloneElement(a.icon, { size: 20 })}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                <label className="block text-slate-400 text-[10px] font-black uppercase tracking-widest">Количество оппонентов</label>
                <div className="flex justify-between items-center bg-slate-950/50 p-3 rounded-2xl border border-slate-800">
                  <button onClick={() => setPlayerCount(Math.max(2, playerCount - 1))} className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 text-xl">-</button>
                  <span className="text-3xl font-black">{playerCount}</span>
                  <button onClick={() => setPlayerCount(Math.min(9, playerCount + 1))} className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 text-xl">+</button>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={startGame} disabled={loading}
            className="w-full bg-gradient-to-r from-green-600 to-emerald-700 hover:from-green-500 hover:to-emerald-600 text-white font-black py-5 rounded-2xl text-xl shadow-xl shadow-green-900/20 transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center uppercase tracking-widest"
          >
            {loading ? "ИНИЦИАЛИЗАЦИЯ..." : <><PlayCircle className="mr-2" /> НАЧАТЬ ТРЕНИРОВКУ</>}
          </button>
        </div>
      </div>
    );
  }

  const isYourTurn = gameState?.players?.[gameState?.current_player_idx]?.is_human;

  const renderCard = (card, size = 'normal') => {
    if (!card) return null;
    if (card === '?') {
      return (
        <div className={`${size === 'small' ? 'w-8 h-12' : 'w-16 md:w-20 h-24 md:h-28'} bg-gradient-to-br from-indigo-600 to-blue-800 rounded-xl border-2 border-white/20 shadow-xl flex items-center justify-center`}>
          <div className="w-full h-full opacity-20 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]"></div>
        </div>
      );
    }

    const suit = card.slice(-1);
    const rank = card.slice(0, -1);
    const isRed = suit === 'H' || suit === 'D';

    const suitSymbols = {
      'H': '♥',
      'D': '♦',
      'C': '♣',
      'S': '♠'
    };

    const cardClasses = size === 'small'
      ? "w-8 h-12 md:w-10 md:h-14 rounded-lg text-[10px] md:text-sm"
      : "w-16 md:w-20 h-24 md:h-28 rounded-xl text-2xl md:text-3xl";

    return (
      <motion.div
        initial={{ rotateY: 90, scale: 0.5, opacity: 0 }}
        animate={{ rotateY: 0, scale: 1, opacity: 1 }}
        className={`${cardClasses} bg-white flex flex-col items-center justify-between p-1.5 md:p-2 text-black shadow-2xl border-b-4 border-slate-300 playing-card`}
      >
        <div className={`self-start font-black leading-none ${isRed ? 'text-red-600' : 'text-slate-900'}`}>{rank}</div>
        <div className={`text-4xl md:text-5xl opacity-80 ${isRed ? 'text-red-600' : 'text-slate-900'}`}>{suitSymbols[suit]}</div>
        <div className={`self-end font-black leading-none rotate-180 ${isRed ? 'text-red-600' : 'text-slate-900'}`}>{rank}</div>
      </motion.div>
    );
  };

  return (
    <div className="h-screen w-full relative overflow-hidden bg-slate-950 flex flex-col text-white font-sans">
      <div className="p-4 px-8 flex justify-between items-center bg-slate-900/50 backdrop-blur-md border-b border-white/5 z-20">
        <div className="flex items-center space-x-8">
          <button onClick={() => setGameStarted(false)} className="text-slate-500 hover:text-white transition-colors"><Home /></button>
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-500 uppercase font-black tracking-widest">Банк</span>
            <div className="flex items-center text-2xl font-black text-yellow-500">
              <Coins size={20} className="mr-2" /> {gameState?.pot}
            </div>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-500 uppercase font-black tracking-widest">Блайнды</span>
            <div className="text-xl font-bold text-slate-200">
              {gameState?.blinds?.[0]} / {gameState?.blinds?.[1]}
            </div>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-500 uppercase font-black tracking-widest">Этап</span>
            <div className="text-xl font-bold text-blue-400 uppercase tracking-tighter">
              {gameState?.phase}
            </div>
          </div>
        </div>

        {gameState?.analysis && (
          <motion.div initial={{ x: 50, opacity: 0 }} animate={{ x: 0, opacity: 1 }}
            className={`flex items-center p-3 px-6 rounded-2xl border ${gameState.analysis.grade === 'Грубая ошибка' ? 'bg-red-500/10 border-red-500/50 text-red-400' :
              gameState.analysis.grade === 'Ошибка' ? 'bg-orange-500/10 border-orange-500/50 text-orange-400' :
                'bg-green-500/10 border-green-500/50 text-green-400'
              }`}
          >
            <BrainCircuit className="mr-3" size={24} />
            <div>
              <div className="text-[10px] font-black uppercase tracking-tighter leading-none mb-1">{gameState.analysis.grade}</div>
              <div className="text-sm font-medium leading-none mb-1">{gameState.analysis.comment}</div>
              {gameState.analysis.recommended && (
                <div className="text-[10px] font-bold uppercase text-slate-400 italic">
                  Рекомендация: <span className="text-white">
                    {gameState.analysis.recommended.toLowerCase().includes('fold') ? 'ПАС' :
                     gameState.analysis.recommended.toLowerCase().includes('call') ? 'КОЛЛ/ЧЕК' : 'РЕЙЗ'}
                  </span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </div>

      <div className="flex-grow flex items-center justify-center p-12 relative">
        <div className="poker-table w-full max-w-6xl aspect-[2.2/1] relative">
          {/* Общие карты */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex space-x-3 z-20">
            <AnimatePresence mode="popLayout">
              {gameState?.community_cards?.map((card, i) => (
                <div key={`${card}-${i}`}>
                  {renderCard(card)}
                </div>
              ))}
            </AnimatePresence>
          </div>

          {/* Игроки */}
          {gameState?.players?.map((player, i) => {
            // Распределение игроков по эллипсу
            const angle = (i * (360 / gameState.players.length) + 90) * (Math.PI / 180);
            const rx = 45; // Радиус по X
            const ry = 40; // Радиус по Y
            const x = Math.cos(angle) * rx + 50;
            const y = Math.sin(angle) * ry + 50;
            const isCurrent = gameState.current_player_idx === i;
            const avatar = AVATARS.find(a => a.id === player.avatar_id) || AVATARS[0];

            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{
                  scale: isCurrent ? 1.05 : 1,
                  opacity: 1,
                  x: "-50%",
                  y: "-50%"
                }}
                style={{ left: `${x}%`, top: `${y}%` }}
                className="absolute flex flex-col items-center z-10"
              >
                <div className={`w-20 h-20 md:w-24 md:h-24 rounded-full border-4 transition-all duration-300 ${isCurrent ? 'border-yellow-400 shadow-[0_0_30px_rgba(250,204,21,0.6)] ring-4 ring-yellow-400/20' :
                  player.is_active ? 'border-green-500/50' : 'border-slate-800 opacity-40'
                  } bg-slate-900 flex items-center justify-center relative shadow-2xl`}>
                  {player.is_human && <div className="absolute -top-4 bg-gradient-to-r from-yellow-400 to-orange-500 text-black text-[8px] md:text-[10px] px-3 py-0.5 rounded-full font-black shadow-lg z-20">ВЫ</div>}
                  <div className="absolute -right-2 top-0 bg-slate-800 border border-white/20 text-[8px] font-black px-1.5 py-0.5 rounded shadow-lg z-20">{player.position}</div>
                  <div className={player.is_active ? 'text-white' : 'text-slate-700'}>
                    {React.cloneElement(avatar.icon, { size: isCurrent ? 48 : 40 })}
                  </div>

                  {/* Ставка игрока */}
                  {player.current_bet > 0 && (
                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      className="absolute -bottom-8 bg-black/60 backdrop-blur-md text-yellow-400 text-[10px] md:text-sm font-black px-3 py-1 rounded-full border border-yellow-400/30 flex items-center shadow-lg"
                    >
                      <Coins size={12} className="mr-1" /> {player.current_bet}
                    </motion.div>
                  )}
                </div>

                <div className="mt-4 bg-slate-900/90 backdrop-blur-md px-3 md:px-4 py-1.5 md:py-2 rounded-2xl border border-white/10 text-center min-w-[100px] md:min-w-[120px] shadow-xl">
                  <div className="text-[8px] md:text-[10px] font-bold text-slate-500 uppercase tracking-tighter truncate">{player.name}</div>
                  <div className="text-sm md:text-lg font-black text-white leading-tight">{player.stack}</div>
                </div>

                {/* Карты игрока */}
                <div className="flex space-x-1 mt-2">
                  <AnimatePresence>
                    {player.hand.map((card, j) => (
                      <div key={`${i}-${j}`}>
                        {renderCard(card, 'small')}
                      </div>
                    ))}
                  </AnimatePresence>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      <AnimatePresence>
        {isYourTurn && (
          <motion.div initial={{ y: 150 }} animate={{ y: 0 }} exit={{ y: 150 }} className="h-44 md:h-48 bg-slate-900/95 backdrop-blur-3xl border-t border-white/10 p-4 md:p-6 flex flex-col items-center justify-center space-y-4 shadow-[0_-20px_50px_rgba(0,0,0,0.5)] z-30">
            <div className="flex items-center space-x-6 mb-2">
              <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Размер рейза</span>
              <input type="range" min={gameState.blinds[1]} max={gameState.players[0].stack} step={10} value={raiseAmount} onChange={(e) => setRaiseAmount(e.target.value)} className="w-48 md:w-80 h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-yellow-500" />
              <div className="flex items-center justify-center bg-slate-950 px-4 py-1.5 rounded-full border border-white/5"><span className="text-lg md:text-2xl font-black text-yellow-500">{raiseAmount}</span></div>
            </div>
            <div className="flex space-x-3 md:space-x-4">
              <ActionButton onClick={() => handleAction('fold')} label="ПАС" color="bg-slate-800 text-slate-400 hover:text-red-400 border-white/5 hover:border-red-500/50" />
              <ActionButton onClick={() => handleAction('call')} label={gameState.current_bet > gameState.players[0].current_bet ? `КОЛЛ ${gameState.current_bet - gameState.players[0].current_bet}` : 'ЧЕК'} color="bg-slate-800 text-white border-white/5 hover:border-blue-500/50" />
              <ActionButton onClick={() => handleAction('raise', raiseAmount)} label={`РЕЙЗ ${raiseAmount}`} color="bg-gradient-to-br from-yellow-500 to-orange-600 text-black shadow-lg shadow-orange-900/20" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      {!isYourTurn && gameStarted && (
        <div className="h-44 md:h-48 bg-slate-950/80 flex items-center justify-center italic text-slate-600 animate-pulse tracking-widest uppercase text-xs">Оппоненты обдумывают ход...</div>
      )}
    </div>
  );
}

function StatCard({ label, value, sub, color = 'text-white' }) {
  return (
    <div className="bg-slate-900/50 backdrop-blur-xl p-6 rounded-[24px] border border-slate-800 text-center shadow-xl">
      <div className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-2">{label}</div>
      <div className={`text-4xl font-black ${color}`}>{value}</div>
      {sub && <div className="text-[10px] text-slate-600 mt-2 uppercase font-black tracking-tighter opacity-50">{sub}</div>}
    </div>
  );
}

function ActionButton({ onClick, label, color }) {
  return (
    <button onClick={onClick} className={`${color} w-32 md:w-48 py-4 md:py-5 rounded-[20px] font-black text-xs md:text-sm tracking-widest border transition-all active:scale-95 uppercase`}>
      {label}
    </button>
  );
}

export default App;
