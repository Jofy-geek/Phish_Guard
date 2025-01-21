"use client";

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Shield, Zap, Lock, AlertTriangle, Play, Pause, Mic, X } from 'lucide-react'

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
    if (probability >= 80) return { level: "High Risk", color: "text-red-500", message: "The current call is suspected of voice phishing. End call." }
    if (probability >= 75) return { level: "Warning", color: "text-orange-500", message: "High probability of voice phishing." }
    if (probability >= 50) return { level: "Caution", color: "text-yellow-500", message: "Moderate probability of phishing." }
    return { level: "Safe", color: "text-green-500", message: "Low probability of phishing." }
  }

  const { level, color, message } = getRiskLevel(phishingProbability);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 font-sans">
      {/* Navigation */}
      <nav className="bg-gray-800 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <a href="#" className="text-2xl font-bold text-blue-400">PhishGuard</a>
            <a href="#" className="hover:text-blue-400 transition-colors">Home</a>
            <a href="#" className="hover:text-blue-400 transition-colors">About</a>
            <a href="#" className="hover:text-blue-400 transition-colors">Contact</a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="container mx-auto py-20 text-center">
        <h1 className="text-5xl font-extrabold mb-6 animate-fade-in-up">
          Protect Your Voice. <span className="text-blue-400">Detect Phishing in Real-Time.</span>
        </h1>
        <p className="text-xl mb-8 animate-fade-in-up animation-delay-200">
          Advanced AI-powered voice phishing detection for the digital age.
        </p>
        <Button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-full transition-all duration-300 transform hover:scale-105 animate-fade-in-up animation-delay-400">
          Get Started
        </Button>
      </header>

      {/* Features Section */}
      <section className="container mx-auto py-20">
        <h2 className="text-3xl font-bold mb-12 text-center">Why Choose VoiceGuard?</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard
            icon={<Shield className="w-12 h-12 text-blue-400" />}
            title="AI-Powered Detection"
            description="Utilizes advanced BERT model for accurate phishing detection."
          />
          <FeatureCard
            icon={<Zap className="w-12 h-12 text-yellow-400" />}
            title="Real-Time Analysis"
            description="Continuous monitoring and analysis of voice conversations for immediate protection."
          />
          <FeatureCard
            icon={<Lock className="w-12 h-12 text-blue-400" />}
            title="Voice Recognition"
            description="Accurate speech-to-text conversion using the Vosk model."
          />
        </div>
      </section>

      {/* Demo Section */}
      <section className="bg-gray-800 py-20">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center">See It In Action</h2>
          <Card className="bg-gray-700 border-gray-600">
            <CardHeader>
              <CardTitle className="text-2xl font-bold text-blue-400">Real-Time Phishing Detection Demo</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center space-y-4">
                <div className="w-full h-40 bg-gray-800 rounded-lg flex flex-col items-center justify-center p-4">
                  {isDetecting ? (
                    <>
                      <Mic className="w-16 h-16 text-blue-400 animate-pulse" />
                      <p className="mt-2 text-sm text-gray-400">Listening...</p>
                    </>
                  ) : (
                    <AlertTriangle className="w-16 h-16 text-gray-600" />
                  )}
                </div>
                <Button
                  className={`${
                    isDetecting ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'
                  } text-white font-bold py-3 px-6 rounded-full transition-all duration-300 transform hover:scale-105`}
                  onClick={handleStartStop}
                >
                  {isDetecting ? (
                    <>
                      <Pause className="w-5 h-5 mr-2" />
                      Stop Detection
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5 mr-2" />
                      Start Detection
                    </>
                  )}
                </Button>
                {isDetecting && (
                  <div className="w-full mt-4">
                    <h3 className="text-lg font-semibold mb-2">Recognized Text:</h3>
                    <p className="bg-gray-800 p-3 rounded">{recognizedText}</p>
                    <h3 className="text-lg font-semibold mt-4 mb-2">Phishing Analysis:</h3>
                    <div className="flex flex-col items-start bg-gray-800 p-3 rounded">
                      <span>Probability: <span className="font-bold">{phishingProbability.toFixed(2)}%</span></span>
                      <span className={`font-bold ${color}`}>{level}</span>
                      <p className="text-sm mt-2">{message}</p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Call to Action */}
      <section className="container mx-auto py-20 text-center">
        <h2 className="text-3xl font-bold mb-6">Ready to Secure Your Voice Communications?</h2>
        <p className="text-xl mb-8">Join thousands of users who trust PhishGuard for real-time phishing protection.</p>
        <Button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-full transition-all duration-300 transform hover:scale-105">
          Start Free Trial
        </Button>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 py-8">
        <div className="container mx-auto text-center">
          <p>&copy; 2024  PhishGuard. All rights reserved.</p>
        </div>
      </footer>

      {/* Phishing Alert Pop-up */}
      {showAlert && (
        <PhishingAlert
          probability={phishingProbability}
          onClose={() => setShowAlert(false)}
        />
      )}
    </div>
  )
}

function FeatureCard({ icon, title, description }) {
  return (
    <Card className="bg-gray-800 border-gray-700 transition-all duration-300 hover:shadow-lg hover:shadow-blue-400/20">
      <CardHeader>
        <div className="mb-4">{icon}</div>
        <CardTitle className="text-xl font-bold">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-gray-400">{description}</p>
      </CardContent>
    </Card>
  )
}

function PhishingAlert({ probability, onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-red-500 flex items-center">
            <AlertTriangle className="w-6 h-6 mr-2" />
            High Risk Phishing Alert!
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-200">
            <X className="w-5 h-5" />
          </button>
        </div>
        <p className="mb-4">A high-risk phishing attempt has been detected!</p>
        <p className="mb-4">Phishing Probability: <span className="font-bold">{probability.toFixed(2)}%</span></p>
        <p className="text-sm text-gray-400 mb-4">The current call is suspected of voice phishing. It is strongly recommended to end the call immediately and report this incident.</p>
        <Button onClick={onClose} className="mt-4 w-full bg-red-600 hover:bg-red-700 text-white">
          Acknowledge and End Call
        </Button>
      </div>
    </div>
  )
}