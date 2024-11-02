import React, { useState, useEffect, useContext } from 'react';
import { Context } from "../store/appContext";
import { format } from 'date-fns';
import "react-day-picker/dist/style.css";
import { Calendar } from './Calendar';


export default AppointmentScheduler = () => {
    const { store, actions } = useContext(Context);
    const [selectedDate, setSelectedDate] = useState(null);
    const [availableSlots, setAvailableSlots] = useState([]);
    const [selectedSlot, setSelectedSlot] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
  
    useEffect(() => {
      if (selectedDate) {
        fetchAvailableSlots(selectedDate);
      }
    }, [selectedDate]);
  
    const fetchAvailableSlots = async (date) => {
      setLoading(true);
      setError(null);
      try {
        const formattedDate = format(date, 'yyyy-MM-dd');
        const response = await fetch(
          `${process.env.BACKEND_URL}/api/appointments/available-slots/${store.userId}?date=${formattedDate}`,
          {
            headers: {
              "Authorization": `Bearer ${sessionStorage.getItem("token")}`
            }
          }
        );
        if (!response.ok) {
          throw new Error('Failed to fetch available slots');
        }
        const data = await response.json();
        setAvailableSlots(data.available_slots);
      } catch (error) {
        console.error("Error fetching slots:", error);
        setError("Failed to load available time slots. Please try again.");
      }
      setLoading(false);
    };
  
    const handleScheduleAppointment = async () => {
      if (!selectedSlot) return;
  
      try {
        const response = await fetch(
          `${process.env.BACKEND_URL}/api/appointments/schedule`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${sessionStorage.getItem("token")}`
            },
            body: JSON.stringify({
              user_id: store.userId,
              datetime: selectedSlot,
              duration: 60
            })
          }
        );
        
        if (!response.ok) {
          throw new Error('Failed to schedule appointment');
        }
  
        const data = await response.json();
        alert("Appointment scheduled successfully!");
        setSelectedSlot(null);
        fetchAvailableSlots(selectedDate);
      } catch (error) {
        console.error("Error scheduling appointment:", error);
        alert("Failed to schedule appointment. Please try again.");
      }
    };
  
    const formatTimeSlot = (isoString) => {
      return new Date(isoString).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
    };
  
    return (
      <div className="max-w-4xl mx-auto p-4">
        <h2 className="text-2xl font-bold mb-4">Schedule an Appointment</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Select a Date</h3>
            <Calendar
              mode="single"
              selected={selectedDate}
              onSelect={setSelectedDate}
              disabled={{ before: new Date() }}
              className="rounded-md border"
            />
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Available Time Slots</h3>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            ) : error ? (
              <div className="text-red-500 text-center py-4">{error}</div>
            ) : availableSlots.length > 0 ? (
              <div className="space-y-2">
                {availableSlots.map((slot) => (
                  <button
                    key={slot}
                    onClick={() => setSelectedSlot(slot)}
                    className={`w-full p-3 text-left rounded transition-colors ${
                      selectedSlot === slot
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    {formatTimeSlot(slot)}
                  </button>
                ))}
              </div>
            ) : selectedDate ? (
              <p className="text-center text-gray-500 py-4">No available slots for this date</p>
            ) : (
              <p className="text-center text-gray-500 py-4">Please select a date to view available slots</p>
            )}
            
            {selectedSlot && (
              <button
                onClick={handleScheduleAppointment}
                className="mt-6 w-full bg-green-500 text-white p-3 rounded hover:bg-green-600 transition-colors"
              >
                Schedule Appointment
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }