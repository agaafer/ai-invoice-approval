// pages/MasterPage.js
import React, { useState, useEffect } from 'react';
import { Switch, Link } from 'react-router-dom';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { format } from 'date-fns';
import axios from 'axios'
import 'reactjs-popup/dist/index.css';

function MasterPage() {
  const [items, setItems] = useState([]);
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const [queueName, setqueueName] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [dropdown, setDropdown] = useState([]);
  
  const [isModalOpen, setIsModalOpen]= useState(false);
  const [selectedItem, setSelectedItem]= useState(null);
  const [note, setNote]= useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {

    try {
      
      const url = process.env.REACT_APP_API_SERVER_URL + 'queues';

      const response = await fetch(url);

      const dropdown_data = await response.json();

      setDropdown(dropdown_data);     

    } catch (error) {
      console.error('Error fetching item details:', error);
    }

  };

  const fetchItems = async () => {
    setIsLoading(true);
    try {
      let url = process.env.REACT_APP_API_SERVER_URL +  'Documents';
      const params = new URLSearchParams();
      if (startDate) {
        params.append('startDate', startDate.toISOString().split('T')[0]);
      }
      if (endDate) {
        params.append('endDate', endDate.toISOString().split('T')[0]);
      }
      if (queueName) {
        params.append('queueName', queueName);
      }
      else
      {
        //params.append('queueName', '301YXB3_02KB3KZLY003ZL1');
        params.append('queueName', dropdown[0].id);
        
      }
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      console.log(url)
      const response = await fetch(url);
      const data = await response.json();
      setItems(data);
    } catch (error) {
      console.error('Error fetching items:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDateChange = (date, setDate) => {
    setDate(date);
  };
  const handleSelectChange = (event) => {
    setqueueName(event.target.value);
    console.log(event.target.value);
  };
  
  //open modal
  const openModal = (item)=>{
    setSelectedItem(item);
    setNote(item.notes || '');
    setIsModalOpen(true);
  };
    //close modal
    const closeModal = ()=>{
      setSelectedItem(null);
      setNote('');
      setIsModalOpen(false);
    };
    //submit note
    const addNote = async ()=>{
      if(!selectedItem) return;
      try {
      
        const url = process.env.REACT_APP_API_SERVER_URL +'Documents/AddNote';
          axios.post(url,{ 
            invoiceNumber: selectedItem.invoiceNumber,
            documentId: selectedItem.id,
            notes: note});
            setItems((prevItems)=> prevItems.map((item)=>item.id === selectedItem.id?{...item,note}:item));
            closeModal();
      }catch (error) {
        console.error('Error adding Notes:', error);
      }
  
    };
  return (
    <div className="px-40 flex flex-1 justify-center py-5">
      <div className="layout-content-container flex flex-col max-w-[1024px] flex-1">
        <div className="flex flex-wrap justify-between gap-3 p-4">
          <p className="text-[#141C24] tracking-light text-[32px] font-bold leading-tight min-w-72">Dashboard</p>
        </div>
        <div className="px-4 py-3 @container">

          <div >
            <label className="block mb-2">Created Start Date</label>
            <DatePicker
              selected={startDate}
              onChange={(date) => handleDateChange(date, setStartDate)}
              selectsStart
              startDate={startDate}
              endDate={endDate}
              maxDate={endDate}
              className="border p-2 rounded"
            />
          </div>
          <div >
            <label className="block mb-2">Created End Date</label>
            <DatePicker
              selected={endDate}
              onChange={(date) => handleDateChange(date, setEndDate)}
              selectsEnd
              startDate={startDate}
              endDate={endDate}
              minDate={startDate}
              className="border p-2 rounded"
            />
          </div>

          <div>
            <label className="block mb-2">Queue Name</label>
            <select onChange={handleSelectChange}>

              {dropdown.map((item) => (
                <option key={item.id} value={item.id} >{item.name}</option>
              ))}

            </select>
          </div>
        </div>
        <div>
          <button
            onClick={fetchItems}
            className="bg-blue-500 text-white px-4 py-2 rounded mx-4"
            disabled={isLoading}>
            {isLoading ? 'Loading...' : 'Retrieve Data'}
          </button>
        </div>

        <div className="px-4 py-3 @container">
          <div className="flex overflow-hidden rounded-xl border border-[#D4DBE8] bg-[#F8F9FB]">
            <table className="table-auto">
              <thead>
                <tr className="bg-[#F8F9FB]">
                  <th style={{ position: "sticky", top: 0, zIndex: 1 }} className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-120 px-4 py-3 text-left text-[#141C24] w-[400px] text-sm font-medium leading-normal">
                    Invoice Number
                  </th>
                  <th style={{ position: "sticky", top: 0, zIndex: 1 }} className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-240 px-4 py-3 text-left text-[#141C24] w-[400px] text-sm font-medium leading-normal">
                    Vendor Name
                  </th>
                  <th style={{ position: "sticky", top: 0, zIndex: 1 }} className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-360 px-4 py-3 text-left text-[#141C24] w-[400px] text-sm font-medium leading-normal">
                    Created Date
                  </th>
                  <th style={{ position: "sticky", top: 0, zIndex: 1 }} className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-360 px-4 py-3 text-left text-[#141C24] w-[400px] text-sm font-medium leading-normal">
                    Invoice Date
                  </th>
                  <th style={{ position: "sticky", top: 0, zIndex: 1 }} className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-480 px-4 py-3 text-left text-[#141C24] w-[400px] text-sm font-medium leading-normal">
                    Invoice Queue
                  </th>
                  <th style={{ position: "sticky", top: 0, zIndex: 1 }} className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-480 px-4 py-3 text-left text-[#141C24] w-[400px] text-sm font-medium leading-normal">
                    Predicted Status
                  </th>
                  <th style={{ position: "sticky", top: 0, zIndex: 1 }} className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-480 px-4 py-3 text-left text-[#141C24] w-[400px] text-sm font-medium leading-normal">
                    Invoice Prediction
                  </th>
                  <th style={{ position: "sticky", top: 0, zIndex: 1 }} className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-600 px-4 py-3 text-left text-[#141C24] w-60 text-[#3F5374] text-sm font-medium leading-normal">
                    Approval Prediction
                  </th>   
                  <th style={{ position: "sticky", top: 0, zIndex: 1 }} className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-480 px-4 py-3 text-left text-[#141C24] w-[400px] text-sm font-medium leading-normal">
                    Notes
                  </th>
                  <th style={{ position: "sticky", top: 0, zIndex: 1 }} className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-480 px-4 py-3 text-left text-[#141C24] w-[400px] text-sm font-medium leading-normal">
                    Actions
                  </th>                                  
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id} className="border-t border-t-[#D4DBE8]">
                    <td className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-120 h-[72px] px-4 py-2 w-[400px] text-[#141C24] text-sm font-normal leading-normal">
                      {item.invoiceNumber}
                    </td>
                    <td className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-240 h-[72px] px-4 py-2 w-[400px] text-[#3F5374] text-sm font-normal leading-normal">
                      {item.vendorName} - {item.vendorID}
                    </td>
                    <td className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-360 h-[72px] px-4 py-2 w-[400px] text-[#3F5374] text-sm font-normal leading-normal">
                      {format(item.createdDateTime, 'yyyy-MM-dd')}
                    </td>
                    <td className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-360 h-[72px] px-4 py-2 w-[400px] text-[#3F5374] text-sm font-normal leading-normal">
                      {format(item.invoiceDate, 'yyyy-MM-dd')}
                    </td>
                    <td className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-480 h-[72px] px-4 py-2 w-[400px] text-[#3F5374] text-sm font-normal leading-normal">
                      {item.queuename}
                    </td>
                    <td className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-480 h-[72px] px-4 py-2 w-[400px] text-[#3F5374] text-sm font-normal leading-normal">

                      <span style={{ backgroundColor: item.name == "Accepted" ? "green" : "red", color: "white" }}> {item.name}
                      </span>
                    </td>

                    <td className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-480 h-[72px] px-4 py-2 w-[400px] text-[#3F5374] text-sm font-normal leading-normal">
                      {item.percent ? item.percent + "%" : ""}
                    </td>
                    <td className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-600 h-[72px] px-4 py-2 w-60 text-[#3F5374] text-sm font-bold leading-normal tracking-[0.015em]">
                      <Link className="text-blue-600 hover:text-blue-500 decoration-2 hover:underline focus:outline-none focus:underline opacity-90" target="_blank" to={`/details/${item.id}`} >
                        See Prediction
                      </Link>
                    </td>  
                    <td className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-480 h-[72px] px-4 py-2 w-[400px] text-[#3F5374] text-sm font-normal leading-normal">
                      {item.notes || 'No Notes'}
                    </td>  
                    <td className="table-914c5686-0d9b-4b5b-8354-a259bbdbd211-column-600 h-[72px] px-4 py-2 w-60 text-[#3F5374] text-sm font-bold leading-normal tracking-[0.015em]">
                    <button className='bg-blue-500 text-white px-4 py-2 rounded mx-4' onClick={() => openModal(item)}>Add Note</button>
                    </td>                                        
                  </tr>

                ))}
              </tbody>
            </table>          
          </div>
        </div>
        <footer className="flex flex-col gap-6 px-5 py-10 text-center @container">
          <div className="flex flex-wrap items-center justify-center gap-6 @[480px]:flex-row @[480px]:justify-around">
            <a className="text-[#3F5374] text-base font-normal leading-normal min-w-40" href="#">Terms of Service</a>
            <a className="text-[#3F5374] text-base font-normal leading-normal min-w-40" href="#">Privacy Policy</a>
            <a className="text-[#3F5374] text-base font-normal leading-normal min-w-40" href="#">System Status</a>
          </div>
          <p className="text-[#3F5374] text-base font-normal leading-normal">@2023 InvoiceAI</p>
        </footer>
        {/* Modal */}
        {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <h2>Add Note for {selectedItem.invoiceNumber}</h2>
            <textarea 
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows="4"
              cols="50"
            />
            <div className="modal-actions">
              <button className='bg-blue-500 text-white px-4 py-2 rounded mx-4' onClick={addNote}>Save</button>
              <button className='bg-red-500 text-white px-4 py-2 rounded mx-4' onClick={closeModal}>Cancel</button>
            </div>
          </div>
        </div>
        )}
        {/* Modal Styles */}
        <style>
        {`
          .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
          }
          .modal-content {
            background: white;
            padding: 20px;
            border-radius: 8px;
            width: 600px;
            text-align: center;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
          }
        `}
      </style>
      </div>
    </div>
  );
}

export default MasterPage;