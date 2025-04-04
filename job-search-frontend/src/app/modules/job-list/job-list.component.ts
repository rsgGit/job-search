import { Component } from '@angular/core';
import {marked} from 'marked';
import { JobServiceService } from '../../job-service.service';
import { LoaderService } from '../../shared/loader/loader.service';
import { countries } from '../countries'
@Component({
  selector: 'app-job-list',
  templateUrl: './job-list.component.html',
  styleUrl: './job-list.component.scss'
})
export class JobListComponent {

  jobs:any = []
  datePostedList:any = [{hours:24, label:'24 hours ago'}, {hours:72, label:'3 days ago'}, {hours:168, label:'1 week ago'},  {hours:210, label:'1 month ago'}]
  selectedJob:any = {}
  searchQuery:any = {keyword:"", location:"", datePosted:""}
  countries:any[] = []
  jobsSearched:any = false

  constructor(private jobService:JobServiceService){

  }

  ngOnInit(){
    this.countries = countries
  }

  getJobs(){
    this.jobsSearched = true
    console.log(this.searchQuery)
    this.jobService.getJobs(this.searchQuery.keyword, this.searchQuery.location, this.searchQuery.datePosted).subscribe({
      next:((res:any)=>{
        console.log(res)
        this.jobs = res
        if(this.jobs.length>0)this.selectJob(this.jobs[0])
      }),
      error:(err=>{
        console.log(err)
      })
    })
  }

  selectJob(job:any){
    job['description'] = marked(job['description'])
    this.selectedJob = job
  }

  goToJobWebsite(){
    window.open(this.selectedJob.job_url, "_blank");
  }

 

}
