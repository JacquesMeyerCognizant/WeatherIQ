'use client';

import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardHeader } from './ui/card';
import { Calendar, Wind, Download, Play, MapPin } from 'lucide-react';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Calendar as CalendarComponent } from './ui/calendar';
import logoImage from 'figma:asset/bc581822bd522a92b95fcc2f3bca92e508ec58fb.png';

export function WeatherIQInterface() {
  const [currentDate] = useState(new Date(2025, 6, 28)); // July 28, 2025
  const [targetDate, setTargetDate] = useState<Date>();
  const [selectedWindfarm, setSelectedWindfarm] = useState('');
  const [turbineCount, setTurbineCount] = useState('');

  const windfarms = [
    'North Sea Alpha',
    'Baltic Beta',
    'Atlantic Gamma',
    'Irish Sea Delta',
    'North Sea Epsilon',
    'Celtic Zeta'
  ];

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-slate-100 p-4">
      <div className="max-w-md mx-auto space-y-6">
        {/* Header */}
        <div className="text-center pt-8 pb-4">
          <div className="flex items-center justify-center mb-4">
            <img 
              src={logoImage} 
              alt="Cognizant Weather IQ" 
              className="h-16 w-auto"
            />
          </div>
          <p className="text-sm text-slate-600">
            Weather Prediction for Offshore Windfarms
          </p>
        </div>

        {/* Main Form Card */}
        <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-blue-600" />
              <h2 className="text-lg font-medium text-slate-800">
                Forecast Parameters
              </h2>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Current Date */}
            <div className="space-y-2">
              <Label htmlFor="current-date" className="text-slate-700">
                Current Date
              </Label>
              <div className="relative">
                <Input
                  id="current-date"
                  value={formatDate(currentDate)}
                  readOnly
                  className="bg-slate-50 border-slate-200 pl-10"
                />
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-500" />
              </div>
            </div>

            {/* Target Date */}
            <div className="space-y-2">
              <Label className="text-slate-700">
                Target Date
              </Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="w-full justify-start bg-white border-slate-200 hover:bg-slate-50"
                  >
                    {targetDate ? formatDate(targetDate) : 'Select target date'}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <CalendarComponent
                    mode="single"
                    selected={targetDate}
                    onSelect={setTargetDate}
                    disabled={(date) => date < currentDate}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>

            {/* Windfarm Selection */}
            <div className="space-y-2">
              <Label className="text-slate-700">
                Select Windfarm
              </Label>
              <Select value={selectedWindfarm} onValueChange={setSelectedWindfarm}>
                <SelectTrigger className="bg-white border-slate-200">
                  <div className="flex items-center gap-2">
                    <Wind className="h-4 w-4 text-slate-500" />
                    <SelectValue placeholder="Choose a windfarm" />
                  </div>
                </SelectTrigger>
                <SelectContent>
                  {windfarms.map((farm) => (
                    <SelectItem key={farm} value={farm}>
                      {farm}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Number of Turbines */}
            <div className="space-y-2">
              <Label htmlFor="turbines" className="text-slate-700">
                Number of Turbines in Operation
              </Label>
              <Input
                id="turbines"
                type="number"
                placeholder="Enter turbine count"
                value={turbineCount}
                onChange={(e) => setTurbineCount(e.target.value)}
                className="bg-white border-slate-200"
                min="1"
                max="500"
              />
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="space-y-3">
          <Button 
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6 text-base"
            disabled={!targetDate || !selectedWindfarm || !turbineCount}
          >
            <Play className="mr-2 h-5 w-5" />
            View Forecast Video
          </Button>
          
          <Button 
            variant="outline" 
            className="w-full border-blue-600 text-blue-600 hover:bg-blue-50 py-6 text-base"
            disabled={!targetDate || !selectedWindfarm || !turbineCount}
          >
            <Download className="mr-2 h-5 w-5" />
            Download Forecast
          </Button>
        </div>

        {/* Footer */}
        <div className="text-center pt-4 pb-8">
          <p className="text-xs text-slate-500">
            Powered by GenCast
          </p>
        </div>
      </div>
    </div>
  );
}