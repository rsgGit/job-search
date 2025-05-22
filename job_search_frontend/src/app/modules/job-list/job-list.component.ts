import { Component, ElementRef, ViewChild } from '@angular/core';
import {marked} from 'marked';
import { JobServiceService } from '../../job-service.service';
import { LoaderService } from '../../shared/loader/loader.service';
import {MatBottomSheet, MatBottomSheetModule, MatBottomSheetRef} from '@angular/material/bottom-sheet';

@Component({
  selector: 'app-job-list',
  templateUrl: './job-list.component.html',
  styleUrl: './job-list.component.scss'
})
export class JobListComponent {

  jobs:any = []
  datePostedList:any = ['24 hours ago', '3 days ago', '1 week ago', '1 month ago']
  selectedJob:any = {}
  searchQuery:any = {keyword:'', location:null, datePosted:null}
  countries:any[] = []
  jobsSearched:any = false
  page = 1;
  pageSize = 0;
  collectionSize = 0;
  isMobileView: boolean = false;
  jobModalRef:MatBottomSheetRef | undefined
  activeFilter: string | null = null;

  constructor(private jobService:JobServiceService, private bottomSheet:MatBottomSheet){

  }

  ngOnInit(){
    this.checkScreenSize();
    window.addEventListener('resize', this.checkScreenSize.bind(this));
    this.getCountries()
  }

  getCountries(){
    this.jobService.getCountries().subscribe({
      next:((res:any)=>{
        this.countries = res
      }),
      error:(err=>{
        console.log(err)
      })
    })
  }

  getJobs(){
    this.jobService.getJobs(this.searchQuery.keyword, this.searchQuery.location==null?'':this.searchQuery.location, this.searchQuery.datePosted==null?'':this.searchQuery.datePosted, this.page).subscribe({
      next:((res:any)=>{
        this.jobs = res.data
        this.page = res.current_page
        this.pageSize = res.results_per_page
        this.collectionSize = res.total
        this.activeFilter = null
        if(this.jobs.length>0){
          this.selectJob(this.jobs[0])
          document.getElementById("scrollContainer")?.scrollTo({ top: 0, behavior: 'smooth' })
        }
        else{
          this.selectedJob = null
          // this.selectedJob.description = 'No jobs found'
        }
        this.jobsSearched = true 
      }),
      error:(err=>{
        console.log(err)
      })
    })
  }

  searchJobs(){
    this.page = 1
    this.getJobs()
  }

  selectJob(job:any){
    job['description'] = marked(job['description'])
    this.selectedJob = job
  }

  goToJobWebsite(){
    window.open(this.selectedJob.url, "_blank");
  }

  enterClick(event:any){
    if(event.key=="Enter") this.searchJobs()
  }
 
  toggleFilter(filter: string) {
    this.activeFilter = this.activeFilter === filter ? null : filter;
  }

  checkScreenSize() {
    this.isMobileView = window.innerWidth <= 1024;
  }

  openModal(job:any, modal:any){
    this.selectJob(job)
    this.bottomSheet.open(modal,
      {
        panelClass: 'full-width'
      })
  }
  
  closeModal(){
    this.bottomSheet.dismiss()
  }

}
