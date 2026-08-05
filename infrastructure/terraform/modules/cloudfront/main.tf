resource "aws_cloudfront_origin_access_control" "website" {
  name                              = "website-${var.environment}"
  description                       = "Access control for private S3 website bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}


resource "aws_cloudfront_distribution" "website" {

  enabled = true

  default_root_object = "index.html"


  origin {

    domain_name = "${var.bucket_name}.s3.amazonaws.com"

    origin_id = "s3-${var.bucket_name}"


    origin_access_control_id = aws_cloudfront_origin_access_control.website.id

  }


  default_cache_behavior {

    allowed_methods = [
      "GET",
      "HEAD"
    ]

    cached_methods = [
      "GET",
      "HEAD"
    ]


    target_origin_id = "s3-${var.bucket_name}"


    viewer_protocol_policy = "redirect-to-https"


    forwarded_values {

      query_string = false

      cookies {
        forward = "none"
      }

    }

  }


  restrictions {

    geo_restriction {

      restriction_type = "none"

    }

  }


  viewer_certificate {

    cloudfront_default_certificate = true

  }


  tags = {

    Environment = var.environment

  }

}
