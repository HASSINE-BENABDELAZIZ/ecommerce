import React, {useEffect, useState} from 'react';
import ReactPaginate from "react-paginate";
import {BrowserRouter, Route, Routes} from "react-router-dom";
import Table from './components/Table'
import SearchBar from "./components/SearchBar";

const App = () => {
    const [visible, setVisible] = React.useState(false);



    const [items, setItems] = useState([]);

    const [pageCount, setpageCount] = useState(0);

    let limit = 100;

    useEffect(() => {
        const getComments = async () => {
            let href = window.location.href.split("/")
            try{
            const res = await fetch(
                `/api/orders/?offset=${(0) * 100}&page=${1}&limit=${limit}`+ href[href.length - 1].replace("?", "&")
            );

            const data = await res.json();
            const total = data.count
            setpageCount(Math.ceil(total / limit));
            setItems(data.results);
            }catch(e){console.log(e); return {}}


        };

        getComments();
    }, [limit]);

    const fetchComments = async (currentPage,search) => {
        try {
        const res = await fetch(
            `/api/orders/?offset=${(currentPage - 1) * 100}&page=${currentPage}&limit=${limit}&search=${search}`


    )


        const data = await res.json();
        const total = data.count
            setpageCount(Math.ceil(total / limit));
        return data.results;
        }
        catch (e){
            console.log(e)
            return {}
            }

    };
    let search_val = React.createRef();
    const handlePageClick = async (data) => {

        let currentPage = data.selected + 1;

        const commentsFormServer = await fetchComments(currentPage,search_val.current.value);
        setItems(commentsFormServer);
    };

    const handeSearch = async () => {
        const commentsFormServer = await fetchComments(1,search_val.current.value);
        setItems(commentsFormServer);

    };

    return (
        <BrowserRouter>
            <Routes>
                <Route exact path='/test/'
                       element={<div><SearchBar refers={search_val} clicks={handeSearch} show_item={visible}/><Table orders={items}/>
                           <ReactPaginate
                               previousLabel={"previous"}
                               nextLabel={"next"}
                               breakLabel={"..."}
                               pageCount={pageCount}
                               marginPagesDisplayed={2}
                               pageRangeDisplayed={3}
                               onPageChange={handlePageClick}
                               containerClassName={"pagination justify-content-center"}
                               pageClassName={"page-item"}
                               pageLinkClassName={"page-link"}
                               previousClassName={"page-item"}
                               previousLinkClassName={"page-link"}
                               nextClassName={"page-item"}
                               nextLinkClassName={"page-link"}
                               breakClassName={"page-item"}
                               breakLinkClassName={"page-link"}
                               activeClassName={"active"}
                           /></div>}
                />


            </Routes>
        </BrowserRouter>
    )
}

export default App
