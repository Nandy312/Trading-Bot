
import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';

const SIGNAL_COLORS = {
  UP: '#27ae60', // green
  DOWN: '#e74c3c', // red
  ANALYZING: '#888', // gray
  NONE: '#222' // black
};

function Dashboard() {
  const [symbols, setSymbols] = useState([]);
  const [selected, setSelected] = useState('');
  const [signal, setSignal] = useState(null);
  const [status, setStatus] = useState('NONE'); // NONE, ANALYZING, UP, DOWN
  const [timer, setTimer] = useState(0);
  const timerRef = useRef();

  useEffect(() => {
    axios.get('http://localhost:8000/assets').then(res => {
      setSymbols(res.data.symbols || []);
      if (res.data.symbols.length > 0) setSelected(res.data.symbols[0].symbol);
    });
  }, []);

  useEffect(() => {
    if (timer > 0) {
      timerRef.current = setTimeout(() => setTimer(timer - 1), 1000);
    }
    return () => clearTimeout(timerRef.current);
  }, [timer]);

  const getSignal = async () => {
    setStatus('ANALYZING');
    setSignal(null);
    setTimer(0);
    // Simulate analysis delay
    setTimeout(async () => {
      try {
        const res = await axios.get(`http://localhost:8000/signal?symbol=${selected}`);
        setSignal(res.data);
        if (res.data.signal === 'BUY') {
          setStatus('UP');
        } else if (res.data.signal === 'SELL') {
          setStatus('DOWN');
        } else {
          setStatus('NONE'); // Show neutral if NO SIGNAL
        }
        setTimer(60); // 1 minute countdown
      } catch {
        setStatus('NONE');
      }
    }, 1500);
  };

  // UI blocks
  return (
    <div style={{
      fontFamily: 'Arial',
      maxWidth: 340,
      margin: '40px auto',
      background: 'rgba(10,10,20,0.95)',
      borderRadius: 18,
      boxShadow: '0 0 24px #0008',
      padding: 24,
      color: '#fff',
      position: 'relative'
    }}>
      {/* Logo */}
      <div style={{textAlign:'center', marginBottom:18}}>
        <div style={{width:60, height:60, margin:'0 auto', background:'#222', borderRadius:16, display:'flex', alignItems:'center', justifyContent:'center'}}>
          <span style={{fontSize:44, color:'#FFD600', fontWeight:'bold'}}>∣∣</span>
        </div>
      </div>
      {/* Asset block */}
      <div style={{background:'#111', borderRadius:10, padding:'10px 0 2px 0', marginBottom:10, textAlign:'center', boxShadow:'0 2px 8px #0004'}}>
        <div style={{fontSize:13, color:'#FFD600', fontWeight:'bold', letterSpacing:1}}>ASSET <span style={{fontSize:11, color:'#fff', fontWeight:'normal'}}> {selected && symbols.find(s=>s.symbol===selected)?.name}</span></div>
        <select value={selected} onChange={e => setSelected(e.target.value)} style={{marginTop:4, background:'#222', color:'#FFD600', fontWeight:'bold', fontSize:18, border:'none', borderRadius:6, padding:'2px 8px'}}>
          {symbols.map(s => (
            <option key={s.symbol} value={s.symbol}>{s.name}</option>
          ))}
        </select>
        <div style={{fontSize:28, color:'#FFD600', fontWeight:'bold', marginTop:2}}>{selected && symbols.find(s=>s.symbol===selected)?.name}</div>
      </div>
      {/* Signal block */}
      <div style={{background: status==='UP'?SIGNAL_COLORS.UP:status==='DOWN'?SIGNAL_COLORS.DOWN:status==='ANALYZING'?SIGNAL_COLORS.ANALYZING:SIGNAL_COLORS.NONE, borderRadius:10, padding:'12px 0', marginBottom:10, textAlign:'center', boxShadow:'0 2px 8px #0004', minHeight:44}}>
        <div style={{fontSize:15, fontWeight:'bold', color:'#fff', letterSpacing:1}}>
          {status==='ANALYZING' ? 'SIGNAL: Analyzing...' : status==='UP' ? 'SIGNAL: UP' : status==='DOWN' ? 'SIGNAL: DOWN' : status==='NONE' ? 'SIGNAL: NO SIGNAL' : ''}
        </div>
        <div style={{fontSize:24, fontWeight:'bold', color:'#fff', marginTop:2}}>
          {status==='ANALYZING' ? 'Analyzing...' : status==='UP' ? 'UP' : status==='DOWN' ? 'DOWN' : status==='NONE' ? 'NO SIGNAL' : ''}
        </div>
      </div>
      {/* Time block */}
      <div style={{background:'#FFD600', borderRadius:10, padding:'10px 0', marginBottom:10, textAlign:'center', color:'#222', fontWeight:'bold', fontSize:22, boxShadow:'0 2px 8px #0004'}}>
        TIME <br/>
        {timer > 0 ? `${Math.floor(timer/60)}:${(timer%60).toString().padStart(2,'0')}` : '1 MINUTE'}
      </div>
      {/* Action block */}
      <div style={{background: timer>0?'#444':'#2d3a3a', borderRadius:10, padding:'10px 0', textAlign:'center', boxShadow:'0 2px 8px #0004'}}>
        <button
          onClick={getSignal}
          disabled={timer>0 || status==='ANALYZING'}
          style={{
            background: timer>0?'#888':'#2ecc40',
            color:'#fff',
            fontWeight:'bold',
            fontSize:20,
            border:'none',
            borderRadius:8,
            padding:'8px 32px',
            cursor: timer>0?'not-allowed':'pointer',
            boxShadow:'0 2px 8px #0004',
            transition:'background 0.2s'
          }}
        >GET SIGNAL</button>
      </div>
    </div>
  );
}

export default Dashboard;
