
document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const video = document.getElementById('boxing-video');
    const timelineContainer = document.getElementById('timeline-container');
    const viewer3dContainer = document.getElementById('viewer-3d');

    // --- Data Storage ---
    let allKeypoints = [];
    let scoreData = [];
    let fps = 30;
    let totalFrames = 0;

    // --- 3D Viewer (Three.js) ---
    let scene, camera, renderer, skeletonGroup;
    const boneConnections = [
        [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5], [5, 6], [6, 8], [9, 10],
        [11, 12], [11, 13], [13, 15], [15, 17], [15, 19], [15, 21],
        [12, 14], [14, 16], [16, 18], [16, 20], [16, 22],
        [11, 23], [12, 24], [23, 24],
        [23, 25], [25, 27], [27, 29], [27, 31],
        [24, 26], [26, 28], [28, 30], [28, 32]
    ]; // MediaPipe BlazePose connections

    // --- D3 Timeline ---
    let svg, xScale, playhead;
    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip");

    // --- INITIALIZATION ---
    async function fetchData() {
        try {
            const response = await fetch('/api/boxing-data');
            if (!response.ok) {
                throw new Error(`Server error: ${response.statusText}`);
            }
            const data = await response.json();
            
            fps = data.keypoints.fps || 30;
            totalFrames = data.keypoints.frames.length;
            allKeypoints = data.keypoints.frames.map(f => f.keypoints_3d);
            scoreData = data.score;
            
            initTimeline();
            init3DViewer();
            setupSync();
        } catch (error) {
            console.error("Failed to fetch data:", error);
            timelineContainer.innerHTML = `<p style="color:red; padding: 10px;">Error loading data. Is the server running and have the data files been generated for boxing.mp4?</p>`;
        }
    }

    function initTimeline() {
        const margin = { top: 20, right: 30, bottom: 30, left: 60 };
        const width = timelineContainer.clientWidth - margin.left - margin.right;
        const height = timelineContainer.clientHeight - margin.top - margin.bottom;

        svg = d3.select(timelineContainer).append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        xScale = d3.scaleLinear()
            .domain([0, totalFrames / fps])
            .range([0, width]);

        const xAxis = d3.axisBottom(xScale);
        svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(xAxis);

        const yLanes = [...new Set(scoreData.map(d => d.target_joint))];
        const yScale = d3.scaleBand()
            .domain(yLanes)
            .range([0, height])
            .padding(0.1);

        const yAxis = d3.axisLeft(yScale);
        svg.append("g").call(yAxis);

        // Pre-process scoreData for de-cluttering
        const processedScoreData = [];
        const lastDisplayedTime = {}; // Stores last displayed time for each joint
        const minTimeGap = 0.1; // Minimum time gap in seconds for displaying direction

        scoreData.sort((a, b) => a.time - b.time);

        scoreData.forEach(d => {
            const joint = d.target_joint;
            if (!lastDisplayedTime[joint] || (d.time - lastDisplayedTime[joint] > minTimeGap)) {
                d.display_direction = true;
                lastDisplayedTime[joint] = d.time;
            } else {
                d.display_direction = false;
            }
            processedScoreData.push(d);
        });

        svg.selectAll(".event")
            .data(processedScoreData)
            .enter()
            .append(d => d.move_type === 'punch' ? document.createElementNS(d3.namespaces.svg, "circle") : document.createElementNS(d3.namespaces.svg, "rect"))
            .attr("class", "event")
            .attr("cx", d => d.move_type === 'punch' ? xScale(d.time) : null)
            .attr("x", d => d.move_type === 'footwork' ? xScale(d.time) - 4 : null)
            .attr("cy", d => d.move_type === 'punch' ? yScale(d.target_joint) + yScale.bandwidth() / 2 : null)
            .attr("y", d => d.move_type === 'footwork' ? yScale(d.target_joint) : null)
            .attr("r", d => d.move_type === 'punch' ? 5 : null)
            .attr("width", d => d.move_type === 'footwork' ? 8 : null)
            .attr("height", d => d.move_type === 'footwork' ? yScale.bandwidth() : null)
            .attr("fill", d => d.move_type === 'punch' ? "red" : "steelblue")
            .on("mouseover", (event, d) => {
                tooltip.transition().duration(200).style("opacity", .9);
                tooltip.html(`<strong>${d.detail}</strong><br/>Time: ${d.time.toFixed(2)}s<br/>${d.velocity ? 'Velocity: ' + d.velocity + ' m/s' : 'Dist: ' + d.distance + ' m'}${d.direction ? '<br/>Direction: ' + d.direction : ''}`)
                    .style("left", (event.pageX + 5) + "px")
                    .style("top", (event.pageY - 28) + "px");
            })
            .on("mouseout", () => {
                tooltip.transition().duration(500).style("opacity", 0);
            });

        // Add direction text for events
        svg.selectAll(".event-direction")
            .data(processedScoreData.filter(d => d.display_direction))
            .enter()
            .append("text")
            .attr("class", "event-direction")
            .attr("font-size", "12px")
            .attr("fill", "#333") // Darker color for better contrast
            .attr("text-anchor", "middle") // Center text horizontally
            .attr("dx", d => d.move_type === 'punch' ? xScale(d.time) : xScale(d.time))
            .attr("dy", d => d.move_type === 'punch' ? yScale(d.target_joint) + yScale.bandwidth() / 2 + 15 : yScale(d.target_joint) + yScale.bandwidth() + 15) // Position below the marker
            .text(d => d.direction || ""); // Display direction if available

        playhead = svg.append("line")
            .attr("class", "playhead")
            .attr("x1", 0).attr("y1", 0)
            .attr("x2", 0).attr("y2", height)
            .attr("stroke", "black")
            .attr("stroke-width", 2);
    }

    function init3DViewer() {
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xffffff);
        
        camera = new THREE.PerspectiveCamera(75, viewer3dContainer.clientWidth / viewer3dContainer.clientHeight, 0.1, 1000);
        camera.position.set(0, 1, 3);

        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(viewer3dContainer.clientWidth, viewer3dContainer.clientHeight);
        viewer3dContainer.appendChild(renderer.domElement);
        
        const gridHelper = new THREE.GridHelper(10, 10);
        scene.add(gridHelper);
        
        skeletonGroup = new THREE.Group();
        scene.add(skeletonGroup);

        // Initial pose
        if(allKeypoints.length > 0) {
            updateSkeletonPose(0);
        }
        
        renderer.render(scene, camera);
    }

    function updateSkeletonPose(frameIndex) {
        if (!allKeypoints[frameIndex]) return;

        // Clear previous skeleton
        while(skeletonGroup.children.length > 0){ 
            skeletonGroup.remove(skeletonGroup.children[0]); 
        }

        const kps = allKeypoints[frameIndex];
        const points = kps.map(p => new THREE.Vector3(p.x, -p.y, -p.z)); // Invert Y and Z for correct orientation

        // Draw joints
        const jointGeometry = new THREE.SphereGeometry(0.03, 16, 16);
        const jointMaterial = new THREE.MeshBasicMaterial({ color: 0x0000ff });
        points.forEach(point => {
            const joint = new THREE.Mesh(jointGeometry, jointMaterial);
            joint.position.copy(point);
            skeletonGroup.add(joint);
        });

        // Draw bones
        const boneMaterial = new THREE.LineBasicMaterial({ color: 0x00ff00 });
        boneConnections.forEach(conn => {
            const startPoint = points[conn[0]];
            const endPoint = points[conn[1]];
            const geometry = new THREE.BufferGeometry().setFromPoints([startPoint, endPoint]);
            const bone = new THREE.Line(geometry, boneMaterial);
            skeletonGroup.add(bone);
        });
    }

    function setupSync() {
        video.addEventListener('timeupdate', () => {
            const currentTime = video.currentTime;
            const currentFrame = Math.floor(currentTime * fps);

            if (xScale) {
                playhead.attr("x1", xScale(currentTime)).attr("x2", xScale(currentTime));
            }
            
            if (scene) {
                updateSkeletonPose(currentFrame);
                renderer.render(scene, camera);
            }
        });
    }

    fetchData();
});
