"use client";

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Shield, Mic, X, Play, Pause } from 'lucide-react'

export default function Component() {
  const [isDetecting, setIsDetecting] = useState(false)
  const [recognizedText, setRecognizedText] = useState("")
  const [phishingProbability, setPhishingProbability] = useState(0)
  const [showAlert, setShowAlert] = useState(false)

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    if (isDetecting) {
      interval = setInterval(async () => {
        const response = await fetch('http://localhost:5000/get_latest');
        const data = await response.json();
        setRecognizedText(data.text);
        setPhishingProbability(data.probability);

        if (data.high_risk_reached) {
          setShowAlert(true);
          setIsDetecting(false);
          await fetch('http://localhost:5000/stop_detection', { method: 'POST' });
        }
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    }
  }, [isDetecting])

  const handleStartStop = async () => {
    if (isDetecting) {
      await fetch('http://localhost:5000/stop_detection', { method: 'POST' });
    } else {
      await fetch('http://localhost:5000/start_detection', { method: 'POST' });
    }
    setIsDetecting(!isDetecting);
  }

  const getRiskLevel = (probability: number) => {
    if (probability >= 80) return { level: "High Risk", color: "text-red-400", bg: "bg-red-950/20" }
    if (probability >= 75) return { level: "Warning", color: "text-orange-400", bg: "bg-orange-950/20" }
    if (probability >= 50) return { level: "Caution", color: "text-yellow-400", bg: "bg-yellow-950/20" }
    return { level: "Safe", color: "text-emerald-400", bg: "bg-emerald-950/20" }
  }

  const { level, color, bg } = getRiskLevel(phishingProbability);

  return (
    <div className="min-h-screen bg-black text-white font-sans">
      {/* Header */}
      <header className="border-b border-white/10">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Shield className="w-6 h-6 text-blue-400" />
            <span className="text-xl font-light">PhishGuard</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          <Card className="bg-white/5 border-white/10">
            <CardContent className="p-6">
              {/* Detection Status */}
              <div className="flex flex-col items-center space-y-6 mb-8">
                <div className={`w-24 h-24 rounded-full flex items-center justify-center ${isDetecting ? 'bg-blue-950/20' : 'bg-white/5'}`}>
                  <Mic className={`w-12 h-12 ${isDetecting ? 'text-blue-400 animate-pulse' : 'text-white/40'}`} />
                </div>
                <Button
                  onClick={handleStartStop}
                  className={`${
                    isDetecting 
                      ? 'bg-red-950/20 text-red-400 hover:bg-red-950/30' 
                      : 'bg-blue-950/20 text-blue-400 hover:bg-blue-950/30'
                  } px-8 py-6 rounded-full text-lg font-light`}
                >
                  {isDetecting ? (
                    <div className="flex items-center space-x-2">
                      <Pause className="w-5 h-5" />
                      <span>Stop</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <Play className="w-5 h-5" />
                      <span>Start</span>
                    </div>
                  )}
                </Button>
              </div>

              {/* Detection Results */}
              {isDetecting && (
                <div className="space-y-6">
                  <div className="space-y-2">
                    <div className="text-sm text-white/60">Recognized Text</div>
                    <div className="bg-white/5 p-4 rounded-lg min-h-[60px]">
                      {recognizedText || "Listening..."}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm text-white/60">Analysis</div>
                    <div className={`${bg} p-4 rounded-lg space-y-2`}>
                      <div className="flex justify-between items-center">
                        <span className={color}>{level}</span>
                        <span className="text-sm">{phishingProbability.toFixed(1)}% Risk</span>
                      </div>
                      <div className="w-full bg-white/10 rounded-full h-2">
                        <div 
                          className={`${color} h-2 rounded-full transition-all duration-500`}
                          style={{ width: `${phishingProbability}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Alert Modal */}
      {showAlert && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-black/80 border border-red-500/20 p-8 rounded-lg max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-6">
              <div className="text-red-400 text-xl font-light">High Risk Detected</div>
              <button onClick={() => setShowAlert(false)} className="text-white/40 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div className="text-white/80">
                A high-risk phishing attempt has been detected with {phishingProbability.toFixed(1)}% probability.
              </div>
              <div className="text-sm text-white/60">
                It is recommended to end the call immediately and report this incident.
              </div>
              <Button
                onClick={() => setShowAlert(false)}
                className="w-full bg-red-950/20 text-red-400 hover:bg-red-950/30"
              >
                Acknowledge
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}