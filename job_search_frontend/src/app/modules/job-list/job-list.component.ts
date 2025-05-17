import { Component } from '@angular/core';
import {marked} from 'marked';
import { JobServiceService } from '../../job-service.service';
import { LoaderService } from '../../shared/loader/loader.service';
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
  
  constructor(private jobService:JobServiceService){

  }

  ngOnInit(){
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
    console.log(this.searchQuery)
    this.jobService.getJobs(this.searchQuery.keyword, this.searchQuery.location==null?'':this.searchQuery.location, this.searchQuery.datePosted==null?'':this.searchQuery.datePosted, this.page).subscribe({
      next:((res:any)=>{
        console.log(res)
        this.jobs = res.data
        this.page = res.current_page
        this.pageSize = res.results_per_page
        this.collectionSize = res.total
        console.log(this.page, this.pageSize, this.collectionSize)
        if(this.jobs.length>0)this.selectJob(this.jobs[0])
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

  selectJob(job:any){
    console.log("selected")
    job['description'] = marked(job['description'])
    this.selectedJob = job
  }

  goToJobWebsite(){
    window.open(this.selectedJob.url, "_blank");
  }

  enterClick(event:any){
    if(event.key=="Enter") this.getJobs()
  }
 

}
